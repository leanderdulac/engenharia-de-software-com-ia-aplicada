"""Gradient accumulation ≡ batch maior com dropout off."""

from __future__ import annotations

from typing import Any

import torch

from dados_sinteticos import lote_contador
from mini_decoder import MiniCfg, MiniDecoder, ce_proximo_token


def _estado(semente: int) -> MiniDecoder:
    torch.manual_seed(semente)
    m = MiniDecoder(MiniCfg())
    return m


def grads_acumulo_vs_batch(
    *,
    micro: int = 4,
    seq: int = 16,
    semente: int = 0,
) -> dict[str, Any]:
    ids = lote_contador(micro, seq, 32, semente=semente + 1)

    a = _estado(semente)
    a.train()  # dropout 0 de qualquer forma (sem Dropout no MiniDecoder)
    opt_a = torch.optim.SGD(a.parameters(), lr=0.0)  # só para zero_grad
    opt_a.zero_grad()
    for i in range(micro):
        loss = ce_proximo_token(a(ids[i : i + 1]), ids[i : i + 1]) / micro
        loss.backward()
    g_ac = {n: p.grad.detach().clone() for n, p in a.named_parameters() if p.grad is not None}

    b = _estado(semente)
    b.train()
    loss_b = ce_proximo_token(b(ids), ids)
    loss_b.backward()
    g_bt = {n: p.grad.detach().clone() for n, p in b.named_parameters() if p.grad is not None}

    deltas = [(g_ac[n] - g_bt[n]).abs().max().item() for n in g_ac]
    return {
        "micro": micro,
        "delta_max": max(deltas) if deltas else 0.0,
        "passou": (max(deltas) if deltas else 0.0) < 1e-5,
        "nota": "média da CE no batch = média das CEs das linhas; dropout ausente",
    }


def treinar_passos(n_passos: int = 40, lr: float = 0.05, semente: int = 0) -> dict[str, Any]:
    torch.manual_seed(semente)
    m = MiniDecoder(MiniCfg())
    opt = torch.optim.AdamW(m.parameters(), lr=lr)
    losses = []
    m.train()
    for i in range(n_passos):
        ids = lote_contador(8, 16, 32, semente=10 + i)
        loss = ce_proximo_token(m(ids), ids)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)
        opt.step()
        losses.append(float(loss.detach()))
    acc = _acuracia_proximo(m)
    return {
        "n_params": m.n_params(),
        "passos": n_passos,
        "loss_ini": losses[0],
        "loss_fim": losses[-1],
        "losses": losses,
        "acuracia_proximo": acc,
        "caiu": losses[-1] < losses[0],
    }


@torch.no_grad()
def _acuracia_proximo(m: MiniDecoder, n: int = 32) -> float:
    m.eval()
    ids = lote_contador(n, 16, 32, semente=99)
    pred = m(ids)[:, :-1].argmax(-1)
    ouro = ids[:, 1:]
    return float((pred == ouro).float().mean())
