from __future__ import annotations

import pytest
import torch

from logps import logprob_complecao
from pares import pares_dpo


@pytest.mark.modelo
def test_logprob_complecao_smol_finita():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from treinar import MODELO

    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    model.eval()
    par = pares_dpo()[0]
    lw, nw = logprob_complecao(model, tok, par["prompt"], par["chosen"], device="cpu")
    ll, nl = logprob_complecao(model, tok, par["prompt"], par["rejected"], device="cpu")
    assert nw > 0 and nl > 0
    assert lw == lw and ll == ll  # não NaN
    assert lw < 0 and ll < 0
