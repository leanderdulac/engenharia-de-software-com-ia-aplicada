from __future__ import annotations

import pytest
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from bancada_latencia import PROMPTS, gerar_lote

pytestmark = pytest.mark.modelo


def test_lote_tem_p50_e_tokens():
    mid = "HuggingFaceTB/SmolLM2-135M"
    tok = AutoTokenizer.from_pretrained(mid)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(mid, dtype=torch.float32)
    r = gerar_lote(model, tok, PROMPTS[:2], max_novos=4, semente=0)
    assert r["n"] == 2
    assert r["latencia_p50_s"] > 0
    assert r["tokens_gerados"] >= 1
