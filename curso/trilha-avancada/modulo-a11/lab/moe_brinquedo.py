"""MoE de brinquedo: 8 experts, router top-k, aux loss estilo Switch.

Não depende do MiniGPT do A3 (ainda esqueleto). A camada é avulsa: embedding de
clusters → MoE → cabeça linear. O ponto pedagógico é *colapso* vs *balanceamento*.
"""

from __future__ import annotations

import math
from typing import Any

import torch
from torch import nn
import torch.nn.functional as F


class ExpertFFN(nn.Module):
    def __init__(self, d: int, d_ff: int):
        super().__init__()
        self.sobe = nn.Linear(d, d_ff)
        self.desce = nn.Linear(d_ff, d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.desce(F.gelu(self.sobe(x)))


class CamadaMoE(nn.Module):
    """Router linear + top-k + FFN por expert. Aux loss: N · Σ f_i P_i (Fedus et al.)."""

    def __init__(self, d: int, n_experts: int = 8, k: int = 2, d_ff: int = 64):
        super().__init__()
        if not (1 <= k <= n_experts):
            raise ValueError("k precisa estar em 1..n_experts")
        self.n_experts = n_experts
        self.k = k
        self.router = nn.Linear(d, n_experts)
        self.experts = nn.ModuleList(ExpertFFN(d, d_ff) for _ in range(n_experts))

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        b, s, d = x.shape
        flat = x.reshape(b * s, d)
        logits = self.router(flat)
        probs = torch.softmax(logits, dim=-1)
        top_val, top_idx = logits.topk(self.k, dim=-1)
        gates = torch.softmax(top_val, dim=-1)

        saida = torch.zeros_like(flat)
        for e, expert in enumerate(self.experts):
            mask = top_idx == e
            if not mask.any():
                continue
            token_idx, slot = mask.nonzero(as_tuple=True)
            y = expert(flat[token_idx])
            saida.index_add_(0, token_idx, y * gates[token_idx, slot].unsqueeze(-1))

        assigned = F.one_hot(top_idx, self.n_experts).sum(dim=-2).clamp(max=1).float()
        f = assigned.mean(dim=0)
        p_medio = probs.mean(dim=0)
        aux = self.n_experts * (f * p_medio).sum()
        return saida.view(b, s, d), aux, f


def parametros_totais_vs_ativos(camada: CamadaMoE) -> dict[str, int]:
    """Totais = router + todos os experts. Ativos por token = router + k experts."""
    n_router = sum(p.numel() for p in camada.router.parameters())
    n_um = sum(p.numel() for p in camada.experts[0].parameters())
    n_experts = n_um * camada.n_experts
    total = n_router + n_experts
    ativos = n_router + n_um * camada.k
    return {
        "router": n_router,
        "um_expert": n_um,
        "todos_experts": n_experts,
        "total": total,
        "ativos_por_token": ativos,
        "fracao_ativa": ativos / total if total else 0,
        "n_experts": camada.n_experts,
        "k": camada.k,
    }


def entropia(f: torch.Tensor) -> float:
    p = f.clamp(min=1e-12)
    p = p / p.sum()
    return float(-(p * p.log()).sum())


def _lote_clusters(n_clusters: int, d: int, batch: int, seq: int, g: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """Cada posição sorteia um cluster; o alvo é o vetor canônico desse cluster."""
    clusters = torch.randint(0, n_clusters, (batch, seq), generator=g)
    centros = torch.eye(n_clusters, d)
    ruido = 0.05 * torch.randn(batch, seq, d, generator=g)
    x = centros[clusters] + ruido
    alvo = centros[clusters]
    return x, alvo


def treinar_moe(
    *,
    n_experts: int = 8,
    k: int = 2,
    d: int = 32,
    d_ff: int = 64,
    passos: int = 250,
    batch: int = 32,
    seq: int = 16,
    aux_coef: float = 0.0,
    vies_expert0: float = 2.5,
    lr: float = 3e-3,
    semente: int = 0,
) -> dict[str, Any]:
    """Dois regimes: ``aux_coef=0`` (colapso típico) vs ``aux_coef>0`` (balanceia)."""
    g = torch.Generator().manual_seed(semente)
    torch.manual_seed(semente)
    moe = CamadaMoE(d, n_experts, k, d_ff)
    with torch.no_grad():
        moe.router.bias.zero_()
        moe.router.bias[0] = vies_expert0
    opt = torch.optim.Adam(moe.parameters(), lr=lr)
    hist_f: list[list[float]] = []
    hist_loss: list[float] = []
    moe.train()
    for _ in range(passos):
        x, alvo = _lote_clusters(n_experts, d, batch, seq, g)
        y, aux, f = moe(x)
        perda = F.mse_loss(y, alvo) + aux_coef * aux
        opt.zero_grad(set_to_none=True)
        perda.backward()
        opt.step()
        hist_f.append(f.detach().tolist())
        hist_loss.append(float(perda.detach()))
    f_final = torch.tensor(hist_f[-1])
    return {
        "aux_coef": aux_coef,
        "vies_expert0": vies_expert0,
        "passos": passos,
        "f_final": hist_f[-1],
        "f_max": float(f_final.max()),
        "f_min": float(f_final.min()),
        "entropia": entropia(f_final),
        "aux_ultimo": float(aux.detach()),
        "mse_ultimo": float(F.mse_loss(y.detach(), alvo)),
        "perda_ultimo": hist_loss[-1],
        "parametros": parametros_totais_vs_ativos(moe),
        "hist_f": hist_f,
    }


def comparar_com_sem_aux(**kwargs) -> dict[str, Any]:
    sem = treinar_moe(aux_coef=0.0, **kwargs)
    com = treinar_moe(aux_coef=0.05, **kwargs)
    return {
        "sem_aux": {k: v for k, v in sem.items() if k != "hist_f"},
        "com_aux": {k: v for k, v in com.items() if k != "hist_f"},
        "hist_f_sem": sem["hist_f"],
        "hist_f_com": com["hist_f"],
        "colapso_sem_aux": sem["f_max"] >= 0.50,
        "mais_equilibrado_com_aux": com["entropia"] > sem["entropia"] and com["f_max"] < sem["f_max"],
    }


def exemplo_numerico_aula() -> dict[str, Any]:
    """2 tokens, 3 experts, top-2 — números da aula, conferidos aqui."""
    logits = torch.tensor([[2.0, 0.0, -1.0], [2.0, 0.5, -1.0]])
    probs = torch.softmax(logits, dim=-1)
    top_val, top_idx = logits.topk(2, dim=-1)
    gates = torch.softmax(top_val, dim=-1)
    assigned = F.one_hot(top_idx, 3).sum(dim=-2).clamp(max=1).float()
    f = assigned.mean(dim=0)
    p_medio = probs.mean(dim=0)
    aux = 3.0 * (f * p_medio).sum()
    return {
        "logits": logits.tolist(),
        "probs": probs.tolist(),
        "top_idx": top_idx.tolist(),
        "gates": gates.tolist(),
        "f": f.tolist(),
        "p_medio": p_medio.tolist(),
        "aux": float(aux),
    }


def histograma_ascii(f: list[float], *, largura: int = 20) -> str:
    linhas = []
    m = max(f) if f else 1.0
    for i, v in enumerate(f):
        n = int(round((v / m) * largura)) if m else 0
        linhas.append(f"E{i:02d} |{'█' * n}{' ' * (largura - n)}| {v:.3f}")
    return "\n".join(linhas)
