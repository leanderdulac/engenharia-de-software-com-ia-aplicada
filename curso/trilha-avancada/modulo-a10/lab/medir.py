"""Qualidade (primeiro inteiro), latência e memória — números do processo, não inventados."""

from __future__ import annotations

import os
import time
from typing import Any

import torch

from tarefas import primeiro_inteiro


def rss_mb() -> float | None:
    try:
        with open("/proc/self/status", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024, 1)
    except OSError:
        return None
    return None


def pegada_mb(model) -> float | None:
    fn = getattr(model, "get_memory_footprint", None)
    if fn is None:
        return None
    return round(fn() / 1e6, 1)


@torch.no_grad()
def avaliar(
    model,
    tok,
    pares: list[dict],
    *,
    device: str = "cpu",
    max_novos: int = 8,
    batch_size: int = 8,
    n_latencia: int = 16,
) -> dict[str, Any]:
    model.eval()
    lado = getattr(tok, "padding_side", "right")
    tok.padding_side = "left"
    comps: list[str] = []
    t_lat: list[float] = []
    try:
        for i in range(0, len(pares), batch_size):
            chunk = pares[i : i + batch_size]
            enc = tok([p["prompt"] for p in chunk], return_tensors="pt", padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            in_len = enc["input_ids"].shape[1]
            t0 = time.perf_counter()
            out = model.generate(
                **enc,
                max_new_tokens=max_novos,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
            dt = time.perf_counter() - t0
            if i < n_latencia:
                t_lat.append(dt / max(len(chunk), 1))
            for row in out:
                comps.append(tok.decode(row[in_len:], skip_special_tokens=True))
    finally:
        tok.padding_side = lado
    acertos = [1.0 if primeiro_inteiro(c) == p["answer"] else 0.0 for c, p in zip(comps, pares)]
    t_lat.sort()
    p50 = t_lat[len(t_lat) // 2] if t_lat else None
    return {
        "n": len(pares),
        "acuracia": float(sum(acertos) / max(len(acertos), 1)),
        "n_acertos": int(sum(acertos)),
        "latencia_p50_s": p50,
        "pegada_mb": pegada_mb(model),
        "rss_processo_mb": rss_mb(),
        "amostra": [
            {"prompt": p["prompt"].strip(), "ouro": p["answer"], "gerado": c, "ok": bool(a)}
            for p, c, a in zip(pares[:4], comps[:4], acertos[:4])
        ],
    }


def gerar_complecoes(model, tok, pares: list[dict], *, device: str = "cpu", max_novos: int = 8) -> list[dict]:
    """Gera compleção greedy por prompt (professor)."""
    model.eval()
    lado = getattr(tok, "padding_side", "right")
    tok.padding_side = "left"
    out_rows: list[dict] = []
    try:
        for i in range(0, len(pares), 8):
            chunk = pares[i : i + 8]
            enc = tok([p["prompt"] for p in chunk], return_tensors="pt", padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            in_len = enc["input_ids"].shape[1]
            gen = model.generate(
                **enc,
                max_new_tokens=max_novos,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
            for p, row in zip(chunk, gen):
                txt = tok.decode(row[in_len:], skip_special_tokens=True)
                out_rows.append({"prompt": p["prompt"], "answer": p["answer"], "complecao": txt})
    finally:
        tok.padding_side = lado
    return out_rows
