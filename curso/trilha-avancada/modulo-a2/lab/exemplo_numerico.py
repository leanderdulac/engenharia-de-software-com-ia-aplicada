"""Exemplo numérico minúsculo da aula — a fonte dos números, não um gabarito de CA2.

Rode: ``python exemplo_numerico.py``. Os valores batem com
``F.scaled_dot_product_attention`` (verificado na autoria).
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from atencao import atencao_produto_interno_escalado
from normas import layer_norm_a_mao, rms_norm


def tensores_da_aula() -> dict[str, torch.Tensor]:
    """Q, K, V 2×2 usados no cálculo à mão (dois tokens, d_k = 2)."""
    q = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    k = torch.tensor([[1.0, 0.0], [1.0, 1.0]])
    v = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    return {"q": q, "k": k, "v": v}


def calcular() -> dict[str, torch.Tensor | float]:
    t = tensores_da_aula()
    q, k, v = t["q"], t["k"], t["v"]
    pontos = q @ k.T
    scaled = pontos / math.sqrt(2.0)
    saida, pesos = atencao_produto_interno_escalado(
        q.unsqueeze(0).unsqueeze(0),
        k.unsqueeze(0).unsqueeze(0),
        v.unsqueeze(0).unsqueeze(0),
        causal=True,
    )
    ref = F.scaled_dot_product_attention(
        q.unsqueeze(0).unsqueeze(0),
        k.unsqueeze(0).unsqueeze(0),
        v.unsqueeze(0).unsqueeze(0),
        is_causal=True,
    )
    x = torch.tensor([1.0, 2.0, 3.0])
    ln, media, desvio = layer_norm_a_mao(x)
    rms_peso = torch.ones(3)
    rms = rms_norm(x, rms_peso)
    return {
        "pontos": pontos,
        "scaled": scaled,
        "pesos": pesos[0, 0],
        "saida": saida[0, 0],
        "ref": ref[0, 0],
        "delta": (saida - ref).abs().max().item(),
        "ln": ln,
        "ln_media": media,
        "ln_desvio": desvio,
        "rms": rms,
    }


def main() -> None:
    torch.set_printoptions(precision=8, sci_mode=False)
    r = calcular()
    print("QK^T\n", r["pontos"])
    print("QK^T / sqrt(2)\n", r["scaled"])
    print("pesos (softmax causal)\n", r["pesos"])
    print("saída nossa\n", r["saida"])
    print("saída F.scaled_dot_product_attention\n", r["ref"])
    print("delta máximo:", r["delta"])
    print("LayerNorm([1,2,3])", r["ln"], "média", r["ln_media"], "desvio", r["ln_desvio"])
    print("RMSNorm([1,2,3])", r["rms"])


if __name__ == "__main__":
    main()
