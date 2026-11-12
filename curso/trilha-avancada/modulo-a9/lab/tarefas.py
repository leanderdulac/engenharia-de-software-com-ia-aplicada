"""Tarefa verificável mínima: aritmética curta, primeiro inteiro da compleção.

Não copia o demo GRPO do M09 (Ollama / sinistro Amplitude). O ouro é a soma.
O prompt termina em ``=`` (sem newline extra): um ``\\n`` depois do igual faz o
SmolLM2-135M base emitir ``A. 10`` em vez de continuar a conta.
"""

from __future__ import annotations

import re
from typing import Any


def _item(a: int, b: int) -> dict[str, Any]:
    return {
        "prompt": f"Responda apenas o numero inteiro.\n{a}+{b}=",
        "answer": str(a + b),
        "a": a,
        "b": b,
    }


def pares_treino() -> list[dict[str, Any]]:
    pares = [(1, 1), (2, 2), (3, 1), (4, 0), (5, 2), (6, 1), (2, 3), (4, 3)]
    return [_item(a, b) for a, b in pares]


def pares_avaliacao() -> list[dict[str, Any]]:
    pares = [(7, 1), (8, 0), (3, 5), (9, 1)]
    return [_item(a, b) for a, b in pares]


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
    """1.0 se o primeiro inteiro da compleção é o ouro (parse verificável).

    Igualdade da string inteira (``strip()==ouro``) quase nunca ocorre em 6
    tokens do base: ele continua (``4\\n\\nA = ``). O parse do primeiro
    inteiro é o sinal de precisão desta aula.
    """
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
    }
