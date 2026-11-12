"""Softmax, temperatura, top-k, top-p e greedy — do zero, conferidos no transformers.

As warpers de top-k / top-p seguem a implementação de
``transformers.generation.logits_process`` (5.22): top-p ordena logits
*crescentes* e corta a cauda com ``cumsum <= 1 - p`` (equivalente ao núcleo
de Holtzman 2019, arXiv:1904.09751).
"""

from __future__ import annotations

import math
from typing import Any

import torch
import torch.nn.functional as F

FILTRO = float("-inf")


def softmax(logits: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Softmax estável: ``exp(z - max) / sum``. Shape livre no ``dim``."""
    z = logits - logits.amax(dim=dim, keepdim=True)
    e = torch.exp(z)
    return e / e.sum(dim=dim, keepdim=True)


def aplicar_temperatura(logits: torch.Tensor, temperatura: float) -> torch.Tensor:
    if temperatura <= 0:
        raise ValueError("temperatura deve ser > 0 (greedy é argmax, não T=0)")
    return logits / temperatura


def aplicar_top_k(logits: torch.Tensor, k: int, *, filtro: float = FILTRO) -> torch.Tensor:
    """Mantém os k maiores logits; o resto vira ``filtro`` (−∞)."""
    if k < 1:
        raise ValueError("k deve ser ≥ 1")
    k = min(k, logits.size(-1))
    limiar = torch.topk(logits, k)[0][..., -1, None]
    return logits.masked_fill(logits < limiar, filtro)


def aplicar_top_p(logits: torch.Tensor, p: float, *, filtro: float = FILTRO) -> torch.Tensor:
    """Núcleo Holtzman / warper HF: massa cumulativa ≥ p, pelo menos 1 token."""
    if not 0.0 < p <= 1.0:
        raise ValueError("p deve estar em (0, 1]")
    # HF 5.22: sort crescente, corta cumsum ≤ 1-p, guarda min_tokens=1 no fim.
    ordenados, idx = torch.sort(logits, descending=False, dim=-1)
    cum = ordenados.softmax(dim=-1).cumsum(dim=-1)
    remover = cum <= (1.0 - p)
    remover[..., -1:] = False
    espalhado = remover.scatter(-1, idx, remover)
    return logits.masked_fill(espalhado, filtro)


def greedy(logits: torch.Tensor) -> torch.Tensor:
    return logits.argmax(dim=-1)


def amostra_categorica(probs: torch.Tensor, gerador: torch.Generator | None = None) -> torch.Tensor:
    return torch.multinomial(probs, num_samples=1, generator=gerador).squeeze(-1)


def preparar_logits(
    logits: torch.Tensor,
    *,
    temperatura: float = 1.0,
    top_k: int | None = None,
    top_p: float | None = None,
) -> torch.Tensor:
    z = aplicar_temperatura(logits, temperatura)
    if top_k is not None:
        z = aplicar_top_k(z, top_k)
    if top_p is not None:
        z = aplicar_top_p(z, top_p)
    return z


def entropia(probs: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """H = −Σ p log p, em nats. Zeros mascarados (0 log 0 → 0)."""
    logp = torch.where(probs > 0, probs.log(), torch.zeros_like(probs))
    return -(probs * logp).sum(dim=dim)


def curva_entropia(logits: torch.Tensor, temperaturas: list[float]) -> list[dict[str, float]]:
    out = []
    log_v = math.log(logits.size(-1))
    for t in temperaturas:
        p = softmax(aplicar_temperatura(logits, t))
        h = float(entropia(p).mean())
        out.append(
            {
                "temperatura": t,
                "entropia_nats": h,
                "entropia_sobre_logV": h / log_v,
            }
        )
    return out


def greedy_autorregressivo(
    model,
    tok,
    prompt: str,
    *,
    max_novos: int = 8,
    device: str = "cpu",
) -> dict[str, Any]:
    """Laço token a token (argmax). Sem cache KV — A11 cobre o cache."""
    model.eval()
    ids = tok(prompt, return_tensors="pt").input_ids.to(device)
    n_prompt = ids.size(1)
    with torch.no_grad():
        for _ in range(max_novos):
            logits = model(ids).logits[:, -1, :]
            nxt = greedy(logits).unsqueeze(-1)
            ids = torch.cat([ids, nxt], dim=-1)
            if tok.eos_token_id is not None and int(nxt) == tok.eos_token_id:
                break
    novos = ids[0, n_prompt:]
    return {
        "ids": ids[0].tolist(),
        "ids_novos": novos.tolist(),
        "texto": tok.decode(novos, skip_special_tokens=True),
        "n_novos": int(novos.numel()),
    }


@torch.no_grad()
def generate_greedy_hf(model, tok, prompt: str, *, max_novos: int = 8, device: str = "cpu"):
    ids = tok(prompt, return_tensors="pt").input_ids.to(device)
    out = model.generate(
        ids,
        max_new_tokens=max_novos,
        do_sample=False,
        pad_token_id=tok.pad_token_id or tok.eos_token_id,
    )
    novos = out[0, ids.size(1) :]
    return {
        "ids": out[0].tolist(),
        "ids_novos": novos.tolist(),
        "texto": tok.decode(novos, skip_special_tokens=True),
    }


def _delta_logits(a: torch.Tensor, b: torch.Tensor) -> float:
    """Compara logits possivelmente com −∞ (inf−inf vira NaN no abs)."""
    ambos_neg_inf = torch.isneginf(a) & torch.isneginf(b)
    finitos = torch.isfinite(a) & torch.isfinite(b)
    if not bool((ambos_neg_inf | finitos).all()):
        return float("inf")
    if not bool(finitos.any()):
        return 0.0
    return float((a[finitos] - b[finitos]).abs().max())


def conferir_warpers_hf(logits: torch.Tensor) -> dict[str, float]:
    """Δ máx vs Temperature / TopK / TopP LogitsWarper do transformers."""
    from transformers.generation.logits_process import (
        TemperatureLogitsWarper,
        TopKLogitsWarper,
        TopPLogitsWarper,
    )

    if logits.dim() == 1:
        scores = logits.unsqueeze(0)
    else:
        scores = logits
    dummy = torch.zeros(scores.size(0), 1, dtype=torch.long)
    t_nossa = aplicar_temperatura(scores, 0.7)
    t_hf = TemperatureLogitsWarper(0.7)(dummy, scores.clone())
    k_nossa = aplicar_top_k(scores, 5)
    k_hf = TopKLogitsWarper(5)(dummy, scores.clone())
    p_nossa = aplicar_top_p(scores, 0.9)
    p_hf = TopPLogitsWarper(0.9)(dummy, scores.clone())
    return {
        "delta_temperatura": _delta_logits(t_nossa, t_hf),
        "delta_top_k": _delta_logits(k_nossa, k_hf),
        "delta_top_p": _delta_logits(p_nossa, p_hf),
    }
