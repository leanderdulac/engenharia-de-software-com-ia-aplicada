import torch

from acumulo import grads_acumulo_vs_batch, treinar_passos
from mini_decoder import MiniCfg, MiniDecoder, ce_proximo_token


def test_shift_ce_shape_e_finita():
    m = MiniDecoder(MiniCfg())
    ids = torch.randint(0, 32, (2, 8))
    logits = m(ids)
    assert logits.shape == (2, 8, 32)
    loss = ce_proximo_token(logits, ids)
    assert torch.isfinite(loss)


def test_tie_nao_conta_lm_duas_vezes():
    m = MiniDecoder(MiniCfg())
    bruto = sum(p.numel() for p in m.parameters())
    # nn.Parameter compartilhado já aparece uma vez em parameters()
    assert m.n_params() == bruto
    assert id(m.lm.weight) == id(m.emb.weight)
    assert m.n_params() == 26240


def test_accumulation_bate_batch():
    r = grads_acumulo_vs_batch()
    assert r["passou"], r["delta_max"]


def test_treino_reduz_loss():
    r = treinar_passos(24, lr=0.08)
    assert r["caiu"]
    assert r["acuracia_proximo"] > 0.5
