"""Inspeção de um MoE real (Granite 1B-A400M). OLMoE 7B: T4, não calibrado aqui.

Se o download/carga falhar ou estourar memória, devolve ``status=nao_coube`` com
a config lida via ``AutoConfig`` — ainda assim o aluno vê 32 experts / 8 ativos.
"""

from __future__ import annotations

import os
import time
import traceback
from typing import Any

import torch

from frases import DOMINIOS

MODELO_GRANITE = "ibm-granite/granite-3.1-1b-a400m-instruct"
MODELO_OLMOE = "allenai/OLMoE-1B-7B-0924-Instruct"


def ler_config_moe(modelo_id: str) -> dict[str, Any]:
    from transformers import AutoConfig

    c = AutoConfig.from_pretrained(modelo_id)
    n_exp = int(getattr(c, "num_local_experts", None) or getattr(c, "num_experts", 0) or 0)
    k = int(getattr(c, "num_experts_per_tok", 0) or 0)
    return {
        "modelo": modelo_id,
        "model_type": c.model_type,
        "arquiteturas": list(getattr(c, "architectures", []) or []),
        "hidden_size": int(c.hidden_size),
        "intermediate_size": int(c.intermediate_size),
        "num_hidden_layers": int(c.num_hidden_layers),
        "num_attention_heads": int(c.num_attention_heads),
        "num_local_experts": n_exp,
        "num_experts_per_tok": k,
        "fracao_experts_ativos": (k / n_exp) if n_exp else None,
        "output_router_logits": bool(getattr(c, "output_router_logits", False)),
        "router_aux_loss_coef": getattr(c, "router_aux_loss_coef", None),
    }


def _contagem_top(router_logits, n_experts: int, k: int) -> torch.Tensor:
    """``router_logits``: tupla por camada, cada uma (tokens, E). Soma hits top-k."""
    hits = torch.zeros(n_experts)
    for layer_logits in router_logits:
        if layer_logits is None:
            continue
        x = layer_logits.detach().float()
        if x.dim() == 3:
            x = x.reshape(-1, x.size(-1))
        _, idx = x.topk(k, dim=-1)
        hits += torch.bincount(idx.reshape(-1).cpu(), minlength=n_experts).float()
    return hits


@torch.no_grad()
def inspecionar_granite(*, max_length: int = 48, device: str | None = None) -> dict[str, Any]:
    cfg = ler_config_moe(MODELO_GRANITE)
    cfg_olmoe = ler_config_moe(MODELO_OLMOE)
    out: dict[str, Any] = {
        "config_granite": cfg,
        "config_olmoe_somente_card": cfg_olmoe,
        "olmoe_status": "nao_calibrado_cpu_7b",
        "status": "ok",
    }
    if os.environ.get("TRILHA_A11_SEM_MOE_REAL"):
        out["status"] = "pulado_env"
        return out

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.perf_counter()
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(MODELO_GRANITE)
        dtype = torch.float32 if device == "cpu" else torch.float16
        model = AutoModelForCausalLM.from_pretrained(
            MODELO_GRANITE,
            dtype=dtype,
            attn_implementation="eager",
            low_cpu_mem_usage=True,
        )
        model.eval()
        model.to(device)
        n_exp = cfg["num_local_experts"]
        k = cfg["num_experts_per_tok"]
        uso: dict[str, list[float]] = {}
        n_params = int(model.num_parameters())
        for dominio, frases in DOMINIOS.items():
            hits = torch.zeros(n_exp)
            n_tok = 0
            for fr in frases:
                ids = tok(fr, return_tensors="pt", truncation=True, max_length=max_length)
                input_ids = ids.input_ids.to(device)
                n_tok += int(input_ids.numel())
                saida = model(
                    input_ids=input_ids,
                    output_router_logits=True,
                    use_cache=False,
                )
                logits = saida.router_logits
                hits += _contagem_top(logits, n_exp, k)
            uso[dominio] = (hits / hits.sum().clamp(min=1)).tolist()
            uso[f"{dominio}_n_tokens"] = n_tok
            uso[f"{dominio}_hits_totais"] = float(hits.sum())

        # hipótese de especialização: a distância entre vetores de uso Auto vs Saúde
        # vs uma permutação aleatória do vetor Saúde (teste tosco, sem p-value de paper)
        u_auto = torch.tensor(uso["auto"])
        u_saude = torch.tensor(uso["saude"])
        u_codigo = torch.tensor(uso["codigo"])
        l1_auto_saude = float((u_auto - u_saude).abs().sum())
        l1_auto_codigo = float((u_auto - u_codigo).abs().sum())
        g = torch.Generator().manual_seed(0)
        perm = u_saude[torch.randperm(n_exp, generator=g)]
        l1_auto_saude_perm = float((u_auto - perm).abs().sum())

        out.update(
            {
                "num_parameters": n_params,
                "device": device,
                "segundos_carga_e_forward": round(time.perf_counter() - t0, 3),
                "uso_por_dominio": {k: v for k, v in uso.items() if not k.endswith("_n_tokens") and not k.endswith("_hits_totais")},
                "tokens_por_dominio": {d: uso[f"{d}_n_tokens"] for d in DOMINIOS},
                "l1_auto_saude": l1_auto_saude,
                "l1_auto_codigo": l1_auto_codigo,
                "l1_auto_saude_permutado": l1_auto_saude_perm,
                "hipotese": (
                    "se Auto e Saúde usam experts de forma diferente, L1(Auto,Saúde) "
                    "deve ser maior que L1(Auto, permutação de Saúde) com alguma folga; "
                    "se não, a especialização por domínio *nesta* amostra não aparece."
                ),
                "especializacao_aparente": l1_auto_saude > l1_auto_saude_perm,
            }
        )
        del model
        return out
    except Exception as e:
        out["status"] = "nao_coube"
        out["erro"] = f"{type(e).__name__}: {e}"
        out["traceback"] = traceback.format_exc()[-2000:]
        out["segundos_ate_falha"] = round(time.perf_counter() - t0, 3)
        return out
