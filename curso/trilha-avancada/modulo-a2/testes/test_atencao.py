from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from atencao import (
    atencao_igual_ao_pytorch,
    atencao_multi_cabeca,
    atencao_produto_interno_escalado,
    juntar_cabecas,
    mascara_causal,
    separar_cabecas,
)


def test_mascara_causal_e_triangular_estrita():
    m = mascara_causal(4, 4)
    assert m.dtype == torch.bool
    assert not m[0, 0]
    assert m[0, 1] and m[0, 2] and m[0, 3]
    assert not m[3, 0] and not m[3, 3]
    assert m.sum().item() == 6  # 3+2+1


def test_sdpa_aleatorio_diff_abaixo_de_1e_menos_5():
    g = torch.Generator().manual_seed(42)
    q = torch.randn(3, 5, 9, 16, generator=g)
    k = torch.randn(3, 5, 9, 16, generator=g)
    v = torch.randn(3, 5, 9, 16, generator=g)
    _, _, delta = atencao_igual_ao_pytorch(q, k, v, causal=True)
    assert delta < 1e-5, delta


def test_sdpa_sem_causal_tambem_bate():
    g = torch.Generator().manual_seed(1)
    q = torch.randn(1, 2, 5, 8, generator=g)
    k = torch.randn(1, 2, 5, 8, generator=g)
    v = torch.randn(1, 2, 5, 8, generator=g)
    nossa, _, delta = atencao_igual_ao_pytorch(q, k, v, causal=False)
    ref = F.scaled_dot_product_attention(q, k, v, is_causal=False)
    assert delta < 1e-5
    assert torch.allclose(nossa, ref, atol=1e-6)


def test_escala_padrao_e_1_sobre_raiz_dk():
    q = torch.ones(1, 1, 2, 4)
    k = torch.ones(1, 1, 2, 4)
    v = torch.arange(8, dtype=torch.float32).view(1, 1, 2, 4)
    saida_auto, _ = atencao_produto_interno_escalado(q, k, v, causal=False)
    saida_exp, _ = atencao_produto_interno_escalado(
        q, k, v, causal=False, escala=1.0 / math.sqrt(4)
    )
    assert torch.equal(saida_auto, saida_exp)


def test_separar_e_juntar_cabecas_inverso():
    x = torch.arange(2 * 3 * 8, dtype=torch.float32).view(2, 3, 8)
    y = juntar_cabecas(separar_cabecas(x, 4))
    assert torch.equal(x, y)


def test_multi_cabeca_shapes_e_causal():
    torch.manual_seed(0)
    b, s, d, h = 2, 6, 12, 3
    x = torch.randn(b, s, d)
    w_q = torch.randn(d, d)
    w_k = torch.randn(d, d)
    w_v = torch.randn(d, d)
    w_o = torch.randn(d, d)
    y, pesos = atencao_multi_cabeca(x, w_q, w_k, w_v, w_o, n_cabecas=h, causal=True)
    assert y.shape == (b, s, d)
    assert pesos.shape == (b, h, s, s)
    assert (pesos[..., 0, 1:] < 1e-6).all()
