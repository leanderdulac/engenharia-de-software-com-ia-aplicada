"""Verificador: aceita a compleção do professor só se o primeiro inteiro é o ouro."""

from __future__ import annotations

from typing import Any

from tarefas import primeiro_inteiro


def aceita(complecao: str, ouro: str) -> bool:
    return primeiro_inteiro(complecao) == str(ouro).strip()


def filtrar(gerados: list[dict[str, Any]]) -> dict[str, Any]:
    ok, rejeitados = [], []
    for g in gerados:
        item = {
            "prompt": g["prompt"],
            "answer": g["answer"],
            "complecao": g["complecao"],
            "r": 1.0 if aceita(g["complecao"], g["answer"]) else 0.0,
        }
        (ok if item["r"] >= 1.0 else rejeitados).append(item)
    return {
        "n_gerados": len(gerados),
        "n_aceitos": len(ok),
        "n_rejeitados": len(rejeitados),
        "taxa_aceite": len(ok) / max(len(gerados), 1),
        "aceitos": ok,
        "rejeitados_amostra": rejeitados[:4],
    }
