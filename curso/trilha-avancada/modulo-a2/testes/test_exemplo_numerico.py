from __future__ import annotations

import torch

from exemplo_numerico import calcular


def test_numeros_da_aula_conferem_com_sdpa_e_com_o_calculo_a_mao():
    r = calcular()
    assert r["delta"] == 0.0 or r["delta"] < 1e-6
    pesos = r["pesos"]
    saida = r["saida"]
    # pos 0: só o próprio token → peso 1 no primeiro, saída = V[0] = (1, 2)
    assert torch.allclose(pesos[0], torch.tensor([1.0, 0.0]), atol=1e-6)
    assert torch.allclose(saida[0], torch.tensor([1.0, 2.0]), atol=1e-6)
    # pos 1: softmax([0, 1/sqrt(2)])
    assert abs(pesos[1, 0].item() - 0.33023846) < 1e-6
    assert abs(pesos[1, 1].item() - 0.66976154) < 1e-6
    assert torch.allclose(saida[1], torch.tensor([2.33952308, 3.33952308]), atol=1e-6)


def test_layernorm_e_rmsnorm_do_vetor_1_2_3():
    r = calcular()
    assert abs(r["ln_media"] - 2.0) < 1e-6
    assert torch.allclose(
        r["ln"], torch.tensor([-1.22473562, 0.0, 1.22473562]), atol=1e-5
    )
    assert torch.allclose(
        r["rms"], torch.tensor([0.46290955, 0.92581910, 1.38872862]), atol=1e-5
    )
