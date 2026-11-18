"""Máscara de resposta, shift causal e escala T² — sem baixar pesos."""

from __future__ import annotations

import torch
import torch.nn.functional as F

from destilar import _kl_mascarada, mascara_shift


def test_mascara_resposta_nao_inclui_prompt():
    # ids: [p0 p1 p2 p3 | c0 c1 c2]  n_prompt=4, n_seq=7
    # logits[:-1] predizem ids[1:] → 6 posições
    # primeira predição da resposta: j = 3 (prediz c0)
    m = mascara_shift(4, 7, "resposta")
    assert m.tolist() == [False, False, False, True, True, True]
    assert not mascara_shift(4, 7, "prompt").any() or (
        mascara_shift(4, 7, "prompt") & m
    ).sum() == 0
    assert mascara_shift(4, 7, "prompt").tolist() == [True, True, True, False, False, False]


def test_mascara_primeiro_so_o_token_inicial_da_resposta():
    m = mascara_shift(4, 7, "primeiro")
    assert m.tolist() == [False, False, False, True, False, False]


def test_shift_alinha_predicao_com_proximo_id():
    n_p, n_seq = 5, 9
    m = mascara_shift(n_p, n_seq, "resposta")
    # posição j prediz ids[j+1]; resposta começa em ids[n_p]
    js = [j for j, bit in enumerate(m.tolist()) if bit]
    previstos = [j + 1 for j in js]
    assert previstos == list(range(n_p, n_seq))


def test_t2_multiplica_kl_por_t_ao_quadrado():
    torch.manual_seed(0)
    s = torch.randn(1, 4, 8)
    t = torch.randn(1, 4, 8)
    mask = torch.tensor([False, True, True, False])
    temp = 2.0
    com = _kl_mascarada(s, t, mask, temp, aplicar_t2=True)
    sem = _kl_mascarada(s, t, mask, temp, aplicar_t2=False)
    assert torch.isfinite(com) and torch.isfinite(sem)
    assert abs(float(com / sem) - temp ** 2) < 1e-5


def test_kl_manual_bate_com_kl_div():
    torch.manual_seed(1)
    s = torch.randn(1, 3, 5)
    t = torch.randn(1, 3, 5)
    mask = torch.ones(3, dtype=torch.bool)
    temp = 2.0
    nossa = _kl_mascarada(s, t, mask, temp, aplicar_t2=True)
    # batchmean em 2-D [n_tok, V] = média do KL por posição (não divide por |V|)
    log_s = F.log_softmax(s[0] / temp, dim=-1)
    p_t = F.softmax(t[0] / temp, dim=-1)
    ref = F.kl_div(log_s, p_t, reduction="batchmean") * (temp ** 2)
    assert torch.allclose(nossa, ref, atol=1e-6)
