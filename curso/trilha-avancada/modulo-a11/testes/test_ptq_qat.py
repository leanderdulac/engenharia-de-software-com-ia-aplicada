from __future__ import annotations

import torch

from ptq import dequantizar_int4, quantizar_int4_por_grupo
from qat import comparar_ptq_qat, fake_quant_int8_ste


def test_int4_roundtrip_erro_limitado():
    torch.manual_seed(0)
    w = torch.randn(12, 64)
    q, scale = quantizar_int4_por_grupo(w, grupo=32)
    rec = dequantizar_int4(q, scale, w.shape, grupo=32)
    rel = (rec - w).abs().mean() / w.abs().mean()
    assert rel < 0.15, rel


def test_int8_ste_e_idempotente_em_multiplos_da_escala():
    w = torch.tensor([0.0, 1.0, -1.0, 2.0])
    q = fake_quant_int8_ste(w)
    assert torch.isfinite(q).all()
    # segunda aplicação não explode
    q2 = fake_quant_int8_ste(q)
    assert torch.isfinite(q2).all()


def test_qat_e_ptq_rodam_e_fp32_e_o_melhor_ou_empate():
    r = comparar_ptq_qat(passos=120, semente=1)
    assert r["mse_fp32"] < 0.5
    assert r["mse_ptq_depois"] >= r["mse_fp32"] - 1e-6
    assert r["mse_qat"] < 1.0
