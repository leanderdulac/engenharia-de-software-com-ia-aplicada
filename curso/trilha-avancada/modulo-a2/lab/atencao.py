"""Atenção: produto interno escalado, máscara causal, multi-cabeça e GQA.

Implementação explícita em PyTorch, para comparar com
``torch.nn.functional.scaled_dot_product_attention``.
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F


def mascara_causal(n_consultas: int, n_chaves: int, *, device=None) -> torch.Tensor:
    """Booleana ``(L, S)``: True = posição bloqueada (o futuro).

    A linha ``i`` só pode olhar as colunas ``0..i`` quando ``L == S``.
    """
    return torch.ones(n_consultas, n_chaves, dtype=torch.bool, device=device).triu(1)


def atencao_produto_interno_escalado(
    consulta: torch.Tensor,
    chave: torch.Tensor,
    valor: torch.Tensor,
    *,
    mascara: torch.Tensor | None = None,
    causal: bool = False,
    escala: float | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Scaled dot-product attention (Vaswani et al. 2017, §3.2.1).

    Shapes, iguais às de ``F.scaled_dot_product_attention``:

    - ``consulta``: ``(..., L, d_k)``
    - ``chave``:    ``(..., S, d_k)``
    - ``valor``:    ``(..., S, d_v)``
    - retorno:     ``(saida (..., L, d_v), pesos (..., L, S))``

    ``mascara`` True significa *não atender* (preenche com ``-inf`` antes do softmax).
    """
    d_k = consulta.size(-1)
    if escala is None:
        escala = 1.0 / math.sqrt(d_k)
    pontos = consulta @ chave.transpose(-2, -1) * escala
    if causal:
        L, S = consulta.size(-2), chave.size(-2)
        pontos = pontos.masked_fill(mascara_causal(L, S, device=pontos.device), float("-inf"))
    if mascara is not None:
        pontos = pontos.masked_fill(mascara, float("-inf"))
    pesos = torch.softmax(pontos, dim=-1)
    saida = pesos @ valor
    return saida, pesos


def atencao_igual_ao_pytorch(
    consulta: torch.Tensor,
    chave: torch.Tensor,
    valor: torch.Tensor,
    *,
    causal: bool = True,
) -> tuple[torch.Tensor, torch.Tensor, float]:
    """Roda a nossa atenção e a de referência; devolve também o |Δ| máximo."""
    nossa, pesos = atencao_produto_interno_escalado(
        consulta, chave, valor, causal=causal
    )
    ref = F.scaled_dot_product_attention(
        consulta, chave, valor, is_causal=causal, dropout_p=0.0
    )
    delta = (nossa - ref).abs().max().item()
    return nossa, pesos, delta


def prova_que_o_futuro_nao_vaza(
    *,
    seq: int = 8,
    d: int = 16,
    cabecas: int = 2,
    semente: int = 0,
    atol: float = 1e-6,
) -> bool:
    """Muda Q/K/V só na última posição; as saídas anteriores têm de ser idênticas."""
    g = torch.Generator().manual_seed(semente)
    forma = (2, cabecas, seq, d)
    q = torch.randn(*forma, generator=g)
    k = torch.randn(*forma, generator=g)
    v = torch.randn(*forma, generator=g)
    out1, _ = atencao_produto_interno_escalado(q, k, v, causal=True)

    q2, k2, v2 = q.clone(), k.clone(), v.clone()
    q2[:, :, -1, :] = 7.0
    k2[:, :, -1, :] = -3.0
    v2[:, :, -1, :] = 11.0
    out2, _ = atencao_produto_interno_escalado(q2, k2, v2, causal=True)
    return torch.allclose(out1[:, :, :-1, :], out2[:, :, :-1, :], atol=atol, rtol=1e-5)


def separar_cabecas(x: torch.Tensor, n_cabecas: int) -> torch.Tensor:
    """``(B, S, D)`` → ``(B, H, S, d_h)`` com ``D = H * d_h``."""
    b, s, d = x.shape
    if d % n_cabecas != 0:
        raise ValueError(f"D={d} não divide H={n_cabecas}")
    d_h = d // n_cabecas
    return x.view(b, s, n_cabecas, d_h).transpose(1, 2).contiguous()


def juntar_cabecas(x: torch.Tensor) -> torch.Tensor:
    """``(B, H, S, d_h)`` → ``(B, S, H*d_h)``."""
    b, h, s, d_h = x.shape
    return x.transpose(1, 2).contiguous().view(b, s, h * d_h)


def repetir_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    """Expande cabeças de K/V para casar com Q no GQA (Ainslie et al. 2023)."""
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    return x[:, :, None, :, :].expand(b, h, n_rep, s, d).reshape(b, h * n_rep, s, d)


def atencao_multi_cabeca(
    x: torch.Tensor,
    w_q: torch.Tensor,
    w_k: torch.Tensor,
    w_v: torch.Tensor,
    w_o: torch.Tensor,
    *,
    n_cabecas: int,
    n_kv: int | None = None,
    causal: bool = True,
    bias_q=None,
    bias_k=None,
    bias_v=None,
    bias_o=None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Uma camada de atenção a partir das matrizes, sem ``nn.MultiheadAttention``.

    ``n_kv is None`` ou ``n_kv == n_cabecas`` → multi-head clássico.
    ``n_kv < n_cabecas`` → grouped-query attention.
    """
    n_kv = n_cabecas if n_kv is None else n_kv
    q = F.linear(x, w_q, bias_q)
    k = F.linear(x, w_k, bias_k)
    v = F.linear(x, w_v, bias_v)
    q = separar_cabecas(q, n_cabecas)
    k = separar_cabecas(k, n_kv)
    v = separar_cabecas(v, n_kv)
    k = repetir_kv(k, n_cabecas // n_kv)
    v = repetir_kv(v, n_cabecas // n_kv)
    contexto, pesos = atencao_produto_interno_escalado(q, k, v, causal=causal)
    saida = F.linear(juntar_cabecas(contexto), w_o, bias_o)
    return saida, pesos
