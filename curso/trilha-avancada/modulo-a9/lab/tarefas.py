"""Tarefa verificável mínima: aritmética curta, primeiro inteiro da compleção.

Não copia o demo GRPO do M09. O ouro é a soma. Pares de treino e de avaliação
são gerados programaticamente, sem sobreposição.
"""

from __future__ import annotations

import os
import re
from typing import Any

N_TREINO = 24
N_EVAL = 80


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
    """Currículo curto (somas ≤ 10, parcelas pequenas) — G>1 tem chance de std≠0."""
    cand = contas(6, 5, 10)
    return [_item(a, b) for a, b in cand[:N_TREINO]]


def pares_avaliacao(n: int | None = None) -> list[dict[str, Any]]:
    n = n if n is not None else int(os.environ.get("TRILHA_A9_N_EVAL", str(N_EVAL)))
    used = {(p["a"], p["b"]) for p in pares_treino()}
    out: list[dict[str, Any]] = []
    for a, b in contas(12, 12, 20):
        if (a, b) in used:
            continue
        out.append(_item(a, b))
        if len(out) >= n:
            break
    return out


def texto_complecao(c: Any) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list) and c:
        last = c[-1]
        if isinstance(last, dict):
            return str(last.get("content", ""))
        return str(last)
    return str(c)


def primeiro_inteiro(texto: str) -> str | None:
    m = re.search(r"-?\d+", texto)
    return m.group(0) if m else None


def recompensa_exata(completions, answer, **kwargs) -> list[float]:
    """1.0 se o primeiro inteiro da compleção é o ouro (parse verificável)."""
    out: list[float] = []
    for c, ouro in zip(completions, answer):
        t = texto_complecao(c)
        gold = str(ouro).strip()
        out.append(1.0 if primeiro_inteiro(t) == gold else 0.0)
    return out


def recompensa_formato(completions, **kwargs) -> list[float]:
    """1.0 se a compleção inteira (strip) é só um inteiro, certo ou errado."""
    out: list[float] = []
    for c in completions:
        t = texto_complecao(c).strip()
        out.append(1.0 if re.fullmatch(r"-?\d+", t) else 0.0)
    return out


def recompensa_hack_digito(completions, **kwargs) -> list[float]:
    """Reward hacking: 1.0 se existe qualquer dígito — '0 aaa' ganha."""
    out: list[float] = []
    for c in completions:
        t = texto_complecao(c)
        out.append(1.0 if re.search(r"\d", t) else 0.0)
    return out


def split_ok() -> dict[str, Any]:
    tr, ev = pares_treino(), pares_avaliacao()
    pt = {p["prompt"] for p in tr}
    pe = {p["prompt"] for p in ev}
    return {
        "n_treino": len(tr),
        "n_eval": len(ev),
        "prompts_disjuntos": pt.isdisjoint(pe),
        "prompt_termina_igual": all(p["prompt"].endswith("=") for p in tr + ev),
        "pares_treino": [(p["a"], p["b"]) for p in tr],
    }


def media_desvio(xs: list[float]) -> dict[str, Any]:
    n = len(xs)
    if n == 0:
        return {"n": 0, "media": None, "desvio": None}
    m = sum(xs) / n
    if n == 1:
        return {"n": 1, "media": float(m), "desvio": 0.0}
    d = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5
    return {"n": n, "media": float(m), "desvio": float(d)}
