"""Gera direto / CoT / self-consistency no SmolLM2. GSM8K não baixado."""

from __future__ import annotations

from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from aritmetica import (
    PARES_EVAL,
    inteiro_apos_resposta,
    motivo_errado,
    prompt_cot,
    prompt_direto,
    voto,
)
from pi_sft import MODELO


@torch.no_grad()
def greedy(model, tok, prefixo: str, *, max_novos: int = 24) -> str:
    device = next(model.parameters()).device
    enc = tok(prefixo, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    n = enc["input_ids"].shape[1]
    out = model.generate(
        **enc,
        max_new_tokens=max_novos,
        do_sample=False,
        pad_token_id=tok.pad_token_id,
    )
    return tok.decode(out[0, n:], skip_special_tokens=True)


def _tok():
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok


def carregar(device: str = "cpu"):
    tok = _tok()
    m = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    m.to(device).eval()
    return m, tok


def _sample(model, tok, prompt: str, *, n: int, temperatura: float, max_novos: int = 24) -> list[str]:
    device = next(model.parameters()).device
    enc = tok(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    n_in = enc["input_ids"].shape[1]
    out = model.generate(
        **enc,
        max_new_tokens=max_novos,
        do_sample=True,
        temperature=temperatura,
        top_p=0.9,
        num_return_sequences=n,
        pad_token_id=tok.pad_token_id,
    )
    return [tok.decode(row[n_in:], skip_special_tokens=True) for row in out]


def avaliar(n_eval: int = 8, n_sc: int = 4, temperatura: float = 0.8) -> dict[str, Any]:
    model, tok = carregar()
    pares = PARES_EVAL[:n_eval]
    linhas = []
    n_dir = n_cot = n_sc_ok = n_motivo = 0
    for a, b in pares:
        ouro = a + b
        p_dir = prompt_direto(a, b)
        p_cot = prompt_cot(a, b)
        g_dir = greedy(model, tok, p_dir, max_novos=12)
        g_cot = greedy(model, tok, p_cot, max_novos=32)
        ams = _sample(model, tok, p_cot, n=n_sc, temperatura=temperatura)
        v = voto(ams)
        pred_dir = inteiro_apos_resposta(g_dir)
        pred_cot = inteiro_apos_resposta(g_cot)
        ok_dir = pred_dir == str(ouro)
        ok_cot = pred_cot == str(ouro)
        ok_sc = v["voto"] == str(ouro)
        errado = motivo_errado(g_cot, a, b, ouro, pred_cot)
        n_dir += int(ok_dir)
        n_cot += int(ok_cot)
        n_sc_ok += int(ok_sc)
        n_motivo += int(errado)
        linhas.append(
            {
                "a": a,
                "b": b,
                "ouro": ouro,
                "direto": g_dir[:80],
                "cot": g_cot[:120],
                "pred_dir": pred_dir,
                "pred_cot": pred_cot,
                "voto": v,
                "ok_dir": ok_dir,
                "ok_cot": ok_cot,
                "ok_sc": ok_sc,
                "certo_motivo_errado": errado,
            }
        )
    n = len(pares)
    return {
        "n": n,
        "n_sc": n_sc,
        "temperatura": temperatura,
        "acc_direto": n_dir / n,
        "acc_cot": n_cot / n,
        "acc_sc": n_sc_ok / n,
        "taxa_certo_motivo_errado": n_motivo / n,
        "cot_piorou": (n_cot / n) < (n_dir / n),
        "linhas": linhas,
    }
