"""LayerNorm (Ba et al. 2016) e RMSNorm (Zhang & Sennrich 2019)."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def layer_norm(
    x: torch.Tensor,
    peso: torch.Tensor | None = None,
    vies: torch.Tensor | None = None,
    eps: float = 1e-5,
) -> torch.Tensor:
    """Normaliza em *features*: média 0, variância 1, depois escala e desloca."""
    return F.layer_norm(x, (x.size(-1),), weight=peso, bias=vies, eps=eps)


def rms_norm(
    x: torch.Tensor,
    peso: torch.Tensor,
    eps: float = 1e-5,
) -> torch.Tensor:
    """RMSNorm: sem centralizar; divide pela raiz da média dos quadrados.

    É o que SmolLM2 / Qwen2.5 / Llama usam dentro do bloco (não o LayerNorm do paper
    de 2017). O cálculo em float32 evita underflow em fp16.
    """
    orig = x.dtype
    x_f = x.float()
    var = x_f.pow(2).mean(dim=-1, keepdim=True)
    y = x_f * torch.rsqrt(var + eps)
    return (y * peso.float()).to(orig)


def layer_norm_a_mao(x: torch.Tensor, eps: float = 1e-5) -> tuple[torch.Tensor, float, float]:
    """Versão didática 1-D: devolve também média e desvio usados."""
    media = x.mean()
    var = x.var(unbiased=False)
    desvio = torch.sqrt(var + eps)
    return (x - media) / desvio, float(media), float(desvio)
