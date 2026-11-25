"""Merge LoRA → denso e confere Δ de logits."""

from __future__ import annotations

from typing import Any

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from pi_sft import MODELO, resolver


@torch.no_grad()
def delta_merge(prompt: str = "### assistant\n", *, max_len: int = 24) -> dict[str, Any]:
    p = resolver()
    if p is None:
        return {"status": "sem_pi_sft", "delta_max": None}
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    peft = PeftModel.from_pretrained(base, str(p))
    peft.eval()
    ids = tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids[:, :max_len]
    z_peft = peft(ids).logits
    merged = peft.merge_and_unload()
    merged.eval()
    z_m = merged(ids).logits
    delta = (z_peft - z_m).abs().max().item()
    return {
        "status": "ok",
        "delta_max": delta,
        "passou": delta < 1e-3,
        "limiar": 1e-3,
        "n_tokens": int(ids.shape[1]),
        "caminho": str(p),
    }
