import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[1] / "lab"
A2 = Path(__file__).resolve().parents[2] / "modulo-a2" / "lab"
for p in (LAB, A2):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


@pytest.fixture(scope="session")
def modelo_pequeno():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    mid = "HuggingFaceTB/SmolLM2-135M"
    tok = AutoTokenizer.from_pretrained(mid)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(mid, dtype=torch.float32)
    model.eval()
    return tok, model, "cpu", mid
