"""Embeddings posicionais: senoides do paper original e RoPE (Su et al. 2021)."""

from __future__ import annotations

import torch


def embeddings_posicionais_sinusoidais(
    seq: int,
    d_model: int,
    *,
    theta: float = 10_000.0,
    device=None,
    dtype=None,
) -> torch.Tensor:
    """PE(pos, 2i) = sin(pos / θ^{2i/d}), PE(pos, 2i+1) = cos(...) — Vaswani et al. §3.5."""
    if d_model % 2 != 0:
        raise ValueError("d_model precisa ser par para o esquema seno/cosseno")
    pos = torch.arange(seq, device=device, dtype=torch.float32).unsqueeze(1)
    i = torch.arange(0, d_model, 2, device=device, dtype=torch.float32)
    div = theta ** (i / d_model)
    angulo = pos / div
    pe = torch.zeros(seq, d_model, device=device, dtype=torch.float32)
    pe[:, 0::2] = torch.sin(angulo)
    pe[:, 1::2] = torch.cos(angulo)
    return pe.to(dtype=dtype or torch.float32)


def rotacionar_metade(x: torch.Tensor) -> torch.Tensor:
    """[-x_{d/2:}, x_{:d/2}] — convenção *não* intercalada (Llama / Qwen / SmolLM2)."""
    m = x.size(-1) // 2
    return torch.cat((-x[..., m:], x[..., :m]), dim=-1)


def aplicar_rope(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    *,
    unsqueeze_dim: int = 1,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Aplica cos/sin de RoPE em Q e K.

    ``cos``/``sin`` vêm com shape ``(B, S, d_h)`` (transformers ≥4.44). Com
    ``unsqueeze_dim=1`` eles transmitem sobre o eixo das cabeças.
    """
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_rot = (q * cos) + (rotacionar_metade(q) * sin)
    k_rot = (k * cos) + (rotacionar_metade(k) * sin)
    return q_rot, k_rot
