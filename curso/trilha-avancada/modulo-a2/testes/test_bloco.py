from __future__ import annotations

import torch

from bloco import BlocoDecoder, MiniDecoder
from posicional import embeddings_posicionais_sinusoidais


def test_bloco_preserva_shape_e_residual_muda_a_entrada():
    torch.manual_seed(0)
    bloco = BlocoDecoder(d_model=8, n_cabecas=2, d_ff=16)
    x = torch.randn(2, 5, 8)
    y, pesos = bloco(x)
    assert y.shape == x.shape
    assert pesos.shape == (2, 2, 5, 5)
    assert not torch.equal(y, x)
    assert (pesos[:, :, 0, 1:] < 1e-6).all()


def test_swiglu_tambem_roda():
    bloco = BlocoDecoder(d_model=8, n_cabecas=2, d_ff=16, swiglu=True)
    y, _ = bloco(torch.randn(1, 3, 8))
    assert y.shape == (1, 3, 8)


def test_minidecoder_logits_e_weight_tying():
    m = MiniDecoder(vocab=20, d_model=8, n_camadas=2, n_cabecas=2, d_ff=16)
    ids = torch.randint(0, 20, (2, 7))
    logits = m(ids)
    assert logits.shape == (2, 7, 20)


def test_senoide_tem_norma_proxima_de_1_por_posicao():
    pe = embeddings_posicionais_sinusoidais(16, 32)
    normas = pe.pow(2).sum(-1).sqrt()
    # cada par sin/cos contribui ~1; d=32 → 16 pares → norma ~ sqrt(16)=4
    assert torch.allclose(normas, torch.full((16,), 4.0), atol=1e-5)
