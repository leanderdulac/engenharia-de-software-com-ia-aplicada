"""Demonstração controlada: a recompensa frouxa aceita lixo que a exata rejeita."""

from __future__ import annotations

from typing import Any

from tarefas import recompensa_exata, recompensa_formato, recompensa_hack_digito


def demonstrar() -> dict[str, Any]:
    # Compleções sintéticas (não geradas): o ponto é o *sinal*, não o modelo.
    completions = ["7", "0", "70", "sete", ""]
    answer = ["7"] * len(completions)
    exata = recompensa_exata(completions, answer)
    formato = recompensa_formato(completions)
    hack = recompensa_hack_digito(completions, answer=answer)
    divergencia = [
        {"texto": t, "exata": e, "hack": h}
        for t, e, h in zip(completions, exata, hack)
        if e != h
    ]
    return {
        "completions": completions,
        "ouro": "7",
        "exata": exata,
        "formato": formato,
        "hack_digito": hack,
        "n_divergencias": len(divergencia),
        "divergencia": divergencia,
        "nota": (
            "hack_digito dá 1.0 a '0' e a '70'; a exata (primeiro inteiro) "
            "só aceita ouro 7. '7 pontos' passaria na exata e falharia no formato estrito."
        ),
    }
