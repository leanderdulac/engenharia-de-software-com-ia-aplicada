"""Duas técnicas já publicadas, reexecutadas no mesmo hardware.

1. A8 — preferência implícita (logps) no hold-out, **sem** retreinar DPO.
2. A11 — PTQ INT8 (lm_head em fp32) vs fp32, perplexidade no corpus curto.
"""

from __future__ import annotations

from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from logps import avaliar_pares
from pares import pares_avaliacao
from pi_sft import MODELO, carregar_base_ou_sft, manifesto
from ptq import perplexidade, quantizar_int8_dinamico
from frases import corpus_ppl


def _base(device: str = "cpu"):
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    m.to(device).eval()
    return m, tok


def tecnica_preferencia(device: str = "cpu") -> dict[str, Any]:
    pares = pares_avaliacao()
    base, tok = _base(device)
    ev_base = avaliar_pares(base, tok, pares, device=device)
    del base
    sft, tok_s, info = carregar_base_ou_sft(device=device, merge=True)
    sft.eval()
    ev_sft = avaliar_pares(sft, tok_s, pares, device=device)
    campos = ("n", "preferencia_bruta", "rewards_accuracies", "margem_media")
    return {
        "modulo": "A8",
        "tecnica": "logps / preferencia implicita (sem DPOTrainer)",
        "ponto_partida": info,
        "base": {k: ev_base[k] for k in campos},
        "pi_sft": {k: ev_sft[k] for k in campos},
        "melhorou": ev_sft["preferencia_bruta"] > ev_base["preferencia_bruta"],
    }


def tecnica_ptq(device: str = "cpu") -> dict[str, Any]:
    m, tok = _base(device)
    textos = corpus_ppl()
    ppl_fp = perplexidade(m, tok, textos, device)
    q, meta = quantizar_int8_dinamico(m, excluir_lm_head=True)
    ppl_i8 = perplexidade(q, tok, textos, "cpu")
    return {
        "modulo": "A11",
        "tecnica": "PTQ INT8 dinamico (lm_head fp32)",
        "ppl_fp32": ppl_fp,
        "ppl_int8": ppl_i8,
        "delta_ppl": ppl_i8 - ppl_fp,
        "int8_piorou": ppl_i8 > ppl_fp,
        "meta": meta,
        "n_textos": len(textos),
    }
