from __future__ import annotations

import pytest
import torch

from destilar import carregar_aluno, diagnosticar_kl, loss_logits, loss_mista, loss_sequencia


@pytest.mark.modelo
def test_loss_sequencia_finita():
    m, tok = carregar_aluno("cpu")
    loss = loss_sequencia(m, tok, "1+1=", "2", "cpu")
    assert torch.isfinite(loss)
    assert loss.item() == loss.item()


@pytest.mark.modelo
def test_loss_mista_e_diagnostico_shift():
    aluno, tok = carregar_aluno("cpu")
    # professor = o próprio aluno congelado: basta para finitude e T²
    aluno.eval()
    prompt, complecao = "1+1=", "2"
    mix = loss_mista(
        aluno,
        aluno,
        tok,
        prompt,
        complecao,
        temperatura=2.0,
        alpha=0.5,
        device="cpu",
    )
    kl = loss_logits(
        aluno, aluno, tok, prompt, complecao, temperatura=2.0, device="cpu"
    )
    ce = loss_sequencia(aluno, tok, prompt, complecao, "cpu")
    assert torch.isfinite(mix) and torch.isfinite(kl) and torch.isfinite(ce)
    d = diagnosticar_kl(aluno, aluno, tok, prompt, complecao, temperatura=2.0)
    assert d["shift_alinhado"]
    assert d["mascara_inclui_prompt"] is False
    assert d["t2_bate"]
    assert d["n_posicoes_kl_resposta"] == d["n_posicoes_ce_resposta"]
    assert d["n_posicoes_kl_resposta"] >= 1
