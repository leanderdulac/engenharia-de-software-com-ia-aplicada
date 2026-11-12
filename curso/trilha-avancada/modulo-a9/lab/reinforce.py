"""REINFORCE de brinquedo: bandit de 4 ações, recompensa 1 só na ação ótima.

Sem LLM. Mostra baseline (média móvel) vs sem baseline. Números saem do JSON.
"""

from __future__ import annotations

from typing import Any

import torch
from torch.distributions import Categorical


def treinar_reinforce(
    *,
    passos: int = 200,
    n_acoes: int = 4,
    otima: int = 1,
    lr: float = 0.25,
    semente: int = 0,
    baseline: bool = True,
) -> dict[str, Any]:
    torch.manual_seed(semente)
    logits = torch.zeros(n_acoes, requires_grad=True)
    opt = torch.optim.SGD([logits], lr=lr)
    hist: list[float] = []
    ema = 0.0
    for _ in range(passos):
        dist = Categorical(logits=logits)
        a = dist.sample()
        r = 1.0 if int(a.item()) == otima else 0.0
        b = ema if baseline else 0.0
        ema = 0.9 * ema + 0.1 * r
        loss = -dist.log_prob(a) * (r - b)
        opt.zero_grad()
        loss.backward()
        opt.step()
        hist.append(r)
    with torch.no_grad():
        probs = torch.softmax(logits, dim=0).tolist()
    k = min(20, passos)
    return {
        "passos": passos,
        "n_acoes": n_acoes,
        "otima": otima,
        "baseline": baseline,
        "recompensa_media_inicio": sum(hist[:k]) / k,
        "recompensa_media_fim": sum(hist[-k:]) / k,
        "p_otima": float(probs[otima]),
        "probs": [float(p) for p in probs],
        "subiu": sum(hist[-k:]) / k > sum(hist[:k]) / k,
    }


def comparar_baseline(passos: int = 200, semente: int = 0) -> dict[str, Any]:
    com = treinar_reinforce(passos=passos, semente=semente, baseline=True)
    sem = treinar_reinforce(passos=passos, semente=semente, baseline=False)
    return {"com_baseline": com, "sem_baseline": sem}
