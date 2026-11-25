"""Somas curtas originais. Não é o GSM8K nem o JSONL do M04."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

PARES_TREINO = ((2, 2), (3, 4), (5, 1), (6, 3), (1, 8))
PARES_EVAL = ((4, 5), (7, 2), (8, 8), (9, 1), (3, 6), (0, 7), (11, 2), (4, 4))


def prompt_direto(a: int, b: int) -> str:
    return f"Responda apenas o numero inteiro.\n{a}+{b}="


def prompt_cot(a: int, b: int) -> str:
    return (
        f"Pense em voz alta em uma linha e termine com Resposta: N.\n{a}+{b}="
    )


def primeiro_inteiro(texto: str) -> str | None:
    m = re.search(r"-?\d+", texto or "")
    return m.group(0) if m else None


def inteiro_apos_resposta(texto: str) -> str | None:
    m = re.search(r"Resposta:\s*(-?\d+)", texto or "", flags=re.I)
    if m:
        return m.group(1)
    return primeiro_inteiro(texto)


def voto(textos: list[str]) -> dict[str, Any]:
    lidos = [inteiro_apos_resposta(t) for t in textos]
    validos = [x for x in lidos if x is not None]
    if not validos:
        return {"voto": None, "n": 0, "dist": {}}
    c = Counter(validos)
    top, n = c.most_common(1)[0]
    return {"voto": top, "n": n, "dist": dict(c), "n_amostras": len(textos)}


def motivo_errado(texto: str, a: int, b: int, ouro: int, pred: str | None) -> bool:
    """Certo no resultado, mas a cadeia não cita as parcelas."""
    if pred != str(ouro):
        return False
    t = texto or ""
    return str(a) not in t or str(b) not in t


def split_ok() -> bool:
    return set(PARES_TREINO).isdisjoint(PARES_EVAL)
