"""Tokenizer real SmolLM2 — marca ``modelo`` (cache da trilha, sem pesos)."""

from __future__ import annotations

import pytest
from transformers import AutoTokenizer

from dialogos_amplitude import SYSTEM, dialogos_treino
from mascarar_sft import IGNORE, lote

pytestmark = pytest.mark.modelo


def test_base_nao_traz_chat_template_e_mascara_fecha():
    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    assert not tok.chat_template
    itens = lote(tok, dialogos_treino()[:1], system=SYSTEM)
    r = itens[0]
    assert all(x == IGNORE for x in r["labels"][: r["n_prompt"]])
    assert r["termina_eos"]
    assert r["n_assistant"] >= 8
