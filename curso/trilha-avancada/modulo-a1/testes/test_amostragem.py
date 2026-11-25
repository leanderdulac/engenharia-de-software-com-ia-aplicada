"""Softmax / temperatura / top-k / top-p sem baixar pesos."""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from amostragem import (
    aplicar_temperatura,
    aplicar_top_k,
    aplicar_top_p,
    conferir_warpers_hf,
    curva_entropia,
    greedy,
    softmax,
)


def test_softmax_bate_com_pytorch():
    g = torch.Generator().manual_seed(0)
    z = torch.randn(4, 9, generator=g)
    assert torch.allclose(softmax(z), F.softmax(z, dim=-1), atol=1e-6)


def test_softmax_estavel_com_logits_grandes():
    z = torch.tensor([[1000.0, 1001.0, 999.0]])
    p = softmax(z)
    assert torch.isfinite(p).all()
    assert abs(float(p.sum()) - 1.0) < 1e-6


def test_temperatura_alta_achata_e_baixa_afina():
    z = torch.tensor([[0.0, 2.0, 4.0]])
    p_fria = softmax(aplicar_temperatura(z, 0.2))
    p_quente = softmax(aplicar_temperatura(z, 5.0))
    assert float(p_fria.max()) > float(p_quente.max())
    # T→0: massa no argmax
    assert int(p_fria.argmax()) == 2


def test_greedy_e_argmax():
    z = torch.tensor([[1.0, 3.0, 2.0], [9.0, 0.0, 1.0]])
    assert greedy(z).tolist() == [1, 0]


def test_top_k_zera_cauda():
    z = torch.tensor([[1.0, 5.0, 3.0, 0.0]])
    out = aplicar_top_k(z, 2)
    assert math.isinf(float(out[0, 0])) and float(out[0, 0]) < 0
    assert math.isinf(float(out[0, 3])) and float(out[0, 3]) < 0
    assert out[0, 1] == 5.0 and out[0, 2] == 3.0


def test_top_p_guarda_pelo_menos_um_token():
    z = torch.tensor([[10.0, -10.0, -10.0, -10.0]])
    out = aplicar_top_p(z, 0.1)
    assert torch.isfinite(out[0, 0])
    assert (out[0, 1:] == float("-inf")).all()


def test_warpers_hf_diff_abaixo_de_1e_menos_5():
    g = torch.Generator().manual_seed(7)
    z = torch.randn(2, 32, generator=g)
    d = conferir_warpers_hf(z)
    assert d["delta_temperatura"] < 1e-5
    assert d["delta_top_k"] < 1e-5
    assert d["delta_top_p"] < 1e-5


def test_entropia_cresce_com_temperatura():
    z = torch.tensor([[0.2, 1.5, -0.3, 0.8]])
    curva = curva_entropia(z, [0.2, 1.0, 3.0])
    hs = [c["entropia_nats"] for c in curva]
    assert hs[0] < hs[1] < hs[2]
    assert hs[-1] < math.log(4) + 1e-6
