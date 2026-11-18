"""CA11.3 — LoRA em experts vs router no MoE de brinquedo (CPU).

O A6 ensinou ``target_modules`` (qv / attn / mlp). Aqui a mesma conta no
MoE: BA no FFN dos experts vs BA só no router. Treino curto, semente fixa.

Granite 1.3B: inspeção da arquitetura em device meta (nomes e params LoRA
teóricos). Treino no Granite = ``nao_calibrado_cpu``. T4 = ``nao_calibrado``.
"""

from __future__ import annotations

import math
from typing import Any

import torch
from torch import nn
import torch.nn.functional as F

from moe_brinquedo import CamadaMoE, _lote_clusters, parametros_totais_vs_ativos

GRANITE_ID = "ibm-granite/granite-3.1-1b-a400m-instruct"
R = 4
ALPHA = 8.0
PASSOS = 80
SEMENTE = 14


class LoRALinear(nn.Module):
    """W + (α/r) BA. Base congelada. A ~ kaiming, B = 0 (Δ inicial nulo)."""

    def __init__(self, base: nn.Linear, r: int = R, alpha: float = ALPHA):
        super().__init__()
        if r < 1:
            raise ValueError("r >= 1")
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False
        self.A = nn.Parameter(torch.empty(r, base.in_features))
        self.B = nn.Parameter(torch.zeros(base.out_features, r))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))
        self.scale = alpha / r

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x) + self.scale * (x @ self.A.T @ self.B.T)

    def n_treino(self) -> int:
        return int(self.A.numel() + self.B.numel())


def _congelar(mod: nn.Module) -> None:
    for p in mod.parameters():
        p.requires_grad = False


def injetar(moe: CamadaMoE, alvos: str) -> dict[str, Any]:
    """alvos: ``experts`` (sobe/desce de todos) ou ``router``."""
    _congelar(moe)
    injetados: list[str] = []
    n = 0
    if alvos == "router":
        moe.router = LoRALinear(moe.router)
        n += moe.router.n_treino()
        injetados.append("router")
    elif alvos == "experts":
        for i, exp in enumerate(moe.experts):
            exp.sobe = LoRALinear(exp.sobe)
            exp.desce = LoRALinear(exp.desce)
            n += exp.sobe.n_treino() + exp.desce.n_treino()
            injetados.append(f"experts.{i}.sobe")
            injetados.append(f"experts.{i}.desce")
    else:
        raise ValueError(alvos)
    return {"alvos": alvos, "modulos": injetados, "n_treino_lora": n, "r": R, "alpha": ALPHA}


def _treinar(alvos: str, *, passos: int = PASSOS, semente: int = SEMENTE) -> dict[str, Any]:
    g = torch.Generator().manual_seed(semente)
    torch.manual_seed(semente)
    moe = CamadaMoE(d=32, n_experts=8, k=2, d_ff=64)
    info = injetar(moe, alvos)
    treino = [p for p in moe.parameters() if p.requires_grad]
    opt = torch.optim.Adam(treino, lr=5e-3)
    moe.train()
    hist: list[float] = []
    for _ in range(passos):
        x, alvo = _lote_clusters(8, 32, 24, 12, g)
        y, _, _ = moe(x)
        perda = F.mse_loss(y, alvo)
        opt.zero_grad(set_to_none=True)
        perda.backward()
        opt.step()
        hist.append(float(perda.detach()))
    densos = parametros_totais_vs_ativos(CamadaMoE(d=32, n_experts=8, k=2, d_ff=64))
    return {
        **info,
        "passos": passos,
        "semente": semente,
        "mse_ini": round(hist[0], 6),
        "mse_fim": round(hist[-1], 6),
        "mse_caiu": hist[-1] < hist[0],
        "n_params_base_moe": densos["total"],
        "fracao_lora": round(info["n_treino_lora"] / densos["total"], 6),
    }


def comparar_experts_vs_router(*, passos: int = PASSOS, semente: int = SEMENTE) -> dict[str, Any]:
    exp = _treinar("experts", passos=passos, semente=semente)
    rot = _treinar("router", passos=passos, semente=semente)
    return {
        "status": "ok",
        "r": R,
        "alpha": ALPHA,
        "passos": passos,
        "semente": semente,
        "experts": exp,
        "router": rot,
        "lora_experts_mais_params": exp["n_treino_lora"] > rot["n_treino_lora"],
        "leitura": (
            "LoRA nos experts atualiza os FFN esparsos (sobe/desce × N). "
            "LoRA no router só mexe em quem é escolhido, não no cálculo do expert. "
            "São alvos diferentes — a lição do A6 (qv vs mlp) no MoE."
        ),
    }


def _lora_numel(out: int, inn: int, r: int) -> int:
    return r * inn + out * r


def inspecionar_granite_alvos(*, r: int = R) -> dict[str, Any]:
    """Arquitetura Granite em meta device: nomes reais, sem treinar, sem 1,3B na RAM.

    Experts **não** são ``nn.Linear``: vêm empacotados em tensores 3D
    ``(n_experts, out, in)``. LoRA padrão do PEFT (A6) não casa com isso.
    """
    try:
        from transformers import AutoConfig, AutoModelForCausalLM
    except Exception as exc:  # pragma: no cover
        return {"status": "nao_calibrado", "motivo": f"transformers: {exc}"}
    try:
        cfg = AutoConfig.from_pretrained(GRANITE_ID)
        with torch.device("meta"):
            modelo = AutoModelForCausalLM.from_config(cfg)
        n_exp = int(getattr(cfg, "num_local_experts", 0) or 0)
        k = int(getattr(cfg, "num_experts_per_tok", 0) or 0)
        amostra: list[str] = []
        n_lora_exp = 0
        n_lora_rot = 0
        n_lora_attn = 0
        n_tensores_expert = 0
        n_tensores_router = 0
        n_lineares_attn = 0
        shapes: dict[str, list] = {"experts": [], "router": []}
        for nome, p in modelo.named_parameters():
            shp = tuple(int(x) for x in p.shape)
            baixo = nome.lower()
            if "block_sparse_moe.experts" in baixo and p.ndim == 3:
                # (n_experts, out, in)
                n_tensores_expert += 1
                n_lora_exp += int(shp[0]) * _lora_numel(shp[1], shp[2], r)
                if len(amostra) < 2:
                    amostra.append(f"{nome}{list(shp)}")
                if len(shapes["experts"]) < 2:
                    shapes["experts"].append({"nome": nome, "shape": list(shp)})
            elif "block_sparse_moe.router" in baixo and p.ndim == 2:
                n_tensores_router += 1
                n_lora_rot += _lora_numel(shp[0], shp[1], r)
                if len(shapes["router"]) < 1:
                    shapes["router"].append({"nome": nome, "shape": list(shp)})
            elif any(s in nome for s in ("q_proj", "k_proj", "v_proj", "o_proj")) and p.ndim == 2:
                n_lineares_attn += 1
                n_lora_attn += _lora_numel(shp[0], shp[1], r)
        del modelo
        return {
            "status": "ok_meta",
            "modelo": GRANITE_ID,
            "num_local_experts": n_exp,
            "num_experts_per_tok": k,
            "n_tensores_expert_3d": n_tensores_expert,
            "n_tensores_router": n_tensores_router,
            "n_lineares_attn": n_lineares_attn,
            "lora_r": r,
            "n_treino_lora_experts": n_lora_exp,
            "n_treino_lora_router": n_lora_rot,
            "n_treino_lora_attn": n_lora_attn,
            "peft_linear_nao_casa_experts_3d": True,
            "amostra_experts": amostra,
            "shapes": shapes,
            "treino": "nao_calibrado_cpu",
            "t4": "nao_calibrado",
            "nota": (
                "from_config(meta): experts são tensores 3D, não Linear. "
                "PEFT target_modules do A6 não aplica BA neles. "
                "Contagem LoRA = r·in + out·r por fatia. Sem treino. T4 nao_calibrado."
            ),
        }
    except Exception as exc:
        return {
            "status": "nao_calibrado",
            "motivo": str(exc)[:400],
            "treino": "nao_calibrado",
            "t4": "nao_calibrado",
        }


def executar_ca11_3() -> dict[str, Any]:
    brinquedo = comparar_experts_vs_router()
    granite = inspecionar_granite_alvos()
    return {
        "status": "ok",
        "motivo": None,
        "a6_publicado": True,
        "brinquedo": brinquedo,
        "granite": granite,
        "t4": "nao_calibrado",
    }
