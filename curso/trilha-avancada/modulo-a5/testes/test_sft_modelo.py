"""SFT curto no SmolLM2 — marca ``modelo``."""

from __future__ import annotations

import pytest

from dialogos_amplitude import SYSTEM, dialogos_treino
from mascarar_sft import lote
from sft_lora import tokenizer, treinar_sft

pytestmark = pytest.mark.modelo


def test_sft_assistant_reduz_loss():
    tok = tokenizer()
    itens = lote(tok, dialogos_treino(), system=SYSTEM)
    r = treinar_sft(itens, passos=2, so_assistant=True, seed=0, salvar_em=None)
    assert r["loss_ini"] is not None
    assert r["loss_fim"] is not None
    assert r["n_params_treino"] > 0
    assert r["n_params_treino"] < r["n_params_total"]
    del r["model"]
