from __future__ import annotations

import torch

from atencao import atencao_produto_interno_escalado, prova_que_o_futuro_nao_vaza


def test_mudar_token_futuro_nao_altera_o_passado():
    assert prova_que_o_futuro_nao_vaza(seq=10, d=8, cabecas=3, semente=7)


def test_sem_mascara_o_futuro_vaza():
    """Controle: se NÃO mascarar, mudar o último V altera a posição 0."""
    torch.manual_seed(0)
    q = torch.randn(1, 1, 4, 8)
    k = torch.randn(1, 1, 4, 8)
    v = torch.randn(1, 1, 4, 8)
    out1, _ = atencao_produto_interno_escalado(q, k, v, causal=False)
    v2 = v.clone()
    v2[:, :, -1, :] += 50
    out2, _ = atencao_produto_interno_escalado(q, k, v2, causal=False)
    assert not torch.allclose(out1[:, :, 0, :], out2[:, :, 0, :], atol=1e-5)


def test_com_mascara_mudar_ultimo_v_nao_mexe_posicao_zero():
    torch.manual_seed(0)
    q = torch.randn(1, 1, 4, 8)
    k = torch.randn(1, 1, 4, 8)
    v = torch.randn(1, 1, 4, 8)
    out1, _ = atencao_produto_interno_escalado(q, k, v, causal=True)
    v2 = v.clone()
    v2[:, :, -1, :] += 50
    out2, _ = atencao_produto_interno_escalado(q, k, v2, causal=True)
    assert torch.allclose(out1[:, :, 0, :], out2[:, :, 0, :], atol=1e-6)
    assert not torch.allclose(out1[:, :, -1, :], out2[:, :, -1, :], atol=1e-5)
