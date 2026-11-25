"""Somas curtas para destilação — pares gerados, treino ≠ eval.

O ouro é a soma. O professor gera a compleção; o verificador filtra.
"""

from __future__ import annotations

import os
import re
from typing import Any

N_TREINO = 32
N_EVAL = 60


def _item(a: int, b: int) -> dict[str, Any]:
    return {
        "prompt": f"Responda apenas o numero inteiro.\n{a}+{b}=",
        "answer": str(a + b),
        "a": a,
        "b": b,
    }


def contas(amax: int, bmax: int, soma_max: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for a in range(0, amax + 1):
        for b in range(0, bmax + 1):
            if a + b <= soma_max:
                out.append((a, b))
    return out


def pares_treino() -> list[dict[str, Any]]:
    return [_item(a, b) for a, b in contas(6, 5, 10)[:N_TREINO]]


def pares_avaliacao(n: int | None = None) -> list[dict[str, Any]]:
    n = n if n is not None else int(os.environ.get("TRILHA_A10_N_EVAL", str(N_EVAL)))
    used = {(p["a"], p["b"]) for p in pares_treino()}
    out: list[dict[str, Any]] = []
    for a, b in contas(12, 12, 20):
        if (a, b) in used:
            continue
        out.append(_item(a, b))
        if len(out) >= n:
            break
    return out


def primeiro_inteiro(texto: str) -> str | None:
    m = re.search(r"-?\d+", texto)
    return m.group(0) if m else None


def split_ok() -> dict[str, Any]:
    tr, ev = pares_treino(), pares_avaliacao()
    return {
        "n_treino": len(tr),
        "n_eval": len(ev),
        "prompts_disjuntos": {p["prompt"] for p in tr}.isdisjoint({p["prompt"] for p in ev}),
    }
