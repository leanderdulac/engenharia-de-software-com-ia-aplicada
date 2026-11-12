"""Diálogos sintéticos no espírito Amplitude. Não leem o JSONL do M09.

oasst1 não é baixado. Treino e eval têm prompts disjuntos.
"""

from __future__ import annotations

from typing import Any

SYSTEM = (
    "Voce extrai JSON com chaves segurado, placa, valor. "
    "valor e float com ponto. Sem prosa."
)


def dialogos_treino() -> list[dict[str, Any]]:
    return [
        {
            "user": "Segurado: Ana Souza. Placa: ABC-1D23. Valor: R$ 1250,00.",
            "assistant": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":1250.00}',
        },
        {
            "user": "Orcamento. Segurado: Bruno Lima. Placa: KLM-4401. Valor: R$ 980,50.",
            "assistant": '{"segurado":"Bruno Lima","placa":"KLM-4401","valor":980.50}',
        },
        {
            "user": "Segurada Carla Dias, placa XYZ-9988, sinistro de 3200 reais.",
            "assistant": '{"segurado":"Carla Dias","placa":"XYZ-9988","valor":3200.00}',
        },
        {
            "user": "Placa FGH-1010. Segurado: Diego Alves. Valor: 75,90.",
            "assistant": '{"segurado":"Diego Alves","placa":"FGH-1010","valor":75.90}',
        },
    ]


def dialogos_eval() -> list[dict[str, Any]]:
    return [
        {
            "user": "Segurado: Eva Martins. Placa: RST-2222. Valor: R$ 410,00.",
            "assistant": '{"segurado":"Eva Martins","placa":"RST-2222","valor":410.00}',
        },
        {
            "user": "Sinistro. Placa: UWW-7777. Segurado Fabio Nunes. 1500,00.",
            "assistant": '{"segurado":"Fabio Nunes","placa":"UWW-7777","valor":1500.00}',
        },
    ]


def split_ok() -> bool:
    u_tr = {d["user"] for d in dialogos_treino()}
    u_ev = {d["user"] for d in dialogos_eval()}
    return u_tr.isdisjoint(u_ev)
