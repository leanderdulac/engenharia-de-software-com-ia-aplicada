"""Pares chosen/rejected originais no espírito Amplitude. Não copiam o JSONL do M09.

Padrão que o M09 ensinou (schema, harness, vírgula decimal) reconstruído com nomes
sintéticos já usados no A2/A11 (`Ana Souza` / `ABC-1D23`). O arquivo
``preference-dataset-amplitude.jsonl`` **não** é lido nem republicado.
"""

from __future__ import annotations

from typing import Any


def pares_dpo() -> list[dict[str, str]]:
    """Lista de dicts ``prompt`` / ``chosen`` / ``rejected`` (formato padrão TRL)."""
    return [
        {
            "prompt": (
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Segurado: Ana Souza. Placa: ABC-1D23. Valor: R$ 1250,00."
            ),
            "chosen": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":1250.00}',
            "rejected": (
                "Com base no texto, a segurada e Ana Souza, a placa e ABC-1D23 e o valor "
                "total do reparo e R$ 1.250,00 (por extenso, sem JSON)."
            ),
        },
        {
            "prompt": (
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Segurado: Ana Souza. Placa: ABC-1D23. Valor: R$ 1250,00."
            ),
            "chosen": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":1250.00}',
            "rejected": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":125000}',
        },
        {
            "prompt": (
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Orcamento: troca de para-choque. Segurado: Bruno Lima. Placa: KLM-4401. Valor: R$ 980,50."
            ),
            "chosen": '{"segurado":"Bruno Lima","placa":"KLM-4401","valor":980.50}',
            "rejected": '{"nome":"Bruno Lima","veiculo":"KLM-4401","preco":"980,50"}',
        },
        {
            "prompt": (
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Sinistro de lataria. Segurado: Carla Dias. Placa: RST-7788. Valor: R$ 320,00."
            ),
            "chosen": '{"segurado":"Carla Dias","placa":"RST-7788","valor":320.00}',
            "rejected": '{"segurado":"Carla Dias","placa":"RST-7788"}',
        },
        {
            "prompt": (
                "Responda so o JSON pedido.\n\n"
                "Segurado: Diego Alves. Placa: FGH-2210. Valor: R$ 4100,00."
            ),
            "chosen": '{"segurado":"Diego Alves","placa":"FGH-2210","valor":4100.00}',
            "rejected": (
                "Claro! Vou te ajudar. Primeiro notei o nome Diego Alves, depois a placa "
                "FGH-2210, e por fim o valor quatro mil e cem reais. Espero ter ajudado :)"
            ),
        },
        {
            "prompt": (
                "Extraia JSON com chaves beneficiario, procedimento, valor.\n\n"
                "Beneficiario: Ana Souza. Procedimento: consulta geriatrica. Valor: R$ 320,00."
            ),
            "chosen": '{"beneficiario":"Ana Souza","procedimento":"consulta geriatrica","valor":320.00}',
            "rejected": "A paciente Ana Souza fez uma consulta. O valor ficou em trezentos e vinte reais.",
        },
        {
            "prompt": (
                "Extraia JSON com chaves beneficiario, procedimento, valor.\n\n"
                "Guia: hemograma. Beneficiario: Elisa Prado. Valor: R$ 85,90."
            ),
            "chosen": '{"beneficiario":"Elisa Prado","procedimento":"hemograma","valor":85.90}',
            "rejected": '{"beneficiario":"Elisa Prado","procedimento":"hemograma","valor":8590}',
        },
        {
            "prompt": "O que e Mixture of Experts, em uma frase, sem chamar de time de agentes.",
            "chosen": "MoE e um FFN com N experts e um router que ativa k deles por token.",
            "rejected": "MoE e um time de agentes que conversam entre si para dividir o trabalho.",
        },
        {
            "prompt": "No LoRA do M09, o que q_proj e v_proj sao?",
            "chosen": "Matrizes de projecao da atencao: consulta e valor.",
            "rejected": "Dois hiperparametros de temperature e top-k no sampler.",
        },
        {
            "prompt": "PTQ acontece quando?",
            "chosen": "Depois do treino, calibrando escalas nos pesos ja prontos.",
            "rejected": "Durante o treino, com straight-through estimator no round.",
        },
        {
            "prompt": "Complete o JSON: {\"placa\":\"ABC-1D23\",\"ok\":",
            "chosen": "true}",
            "rejected": "\"talvez, depende da oficina e do perito e de uma analise longa\"}",
        },
        {
            "prompt": "Devolva so o numero do valor em ponto: R$ 1250,00",
            "chosen": "1250.00",
            "rejected": "125000",
        },
    ]


def pares_kto() -> list[dict[str, Any]]:
    """Converte cada par em dois exemplos KTO (label True/False)."""
    out: list[dict[str, Any]] = []
    for p in pares_dpo():
        out.append({"prompt": p["prompt"], "completion": p["chosen"], "label": True})
        out.append({"prompt": p["prompt"], "completion": p["rejected"], "label": False})
    return out


def estatistica_comprimento(pares: list[dict[str, str]] | None = None) -> dict[str, Any]:
    pares = pares or pares_dpo()
    ch = [len(p["chosen"]) for p in pares]
    rj = [len(p["rejected"]) for p in pares]
    n = len(pares)
    return {
        "n": n,
        "chosen_chars_medio": sum(ch) / n,
        "rejected_chars_medio": sum(rj) / n,
        "razao_rejected_sobre_chosen": (sum(rj) / n) / max(sum(ch) / n, 1e-9),
        "rejeitado_mais_longo": sum(rj) / n > sum(ch) / n,
        "nota": (
            "rejeitados em prosa sao mais longos; DPO sem normalizar por |y| "
            "pode aprender 'seja curto', nao so 'seja JSON'"
        ),
    }
