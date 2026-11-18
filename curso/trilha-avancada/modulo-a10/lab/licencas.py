"""Licenças conferidas nos cards Hugging Face (nov/2026). Não inventar."""

from __future__ import annotations

from typing import Any

PROFESSOR = "HuggingFaceTB/SmolLM2-360M"
ALUNO = "HuggingFaceTB/SmolLM2-135M"
QWEN_ALT = "Qwen/Qwen2.5-0.5B"


def manifesto() -> dict[str, Any]:
    return {
        "professor": {
            "id": PROFESSOR,
            "licenca_card": "Apache-2.0",
            "card": "https://huggingface.co/HuggingFaceTB/SmolLM2-360M",
            "conferido": "2026-11-12",
        },
        "aluno": {
            "id": ALUNO,
            "licenca_card": "Apache-2.0",
            "card": "https://huggingface.co/HuggingFaceTB/SmolLM2-135M",
            "conferido": "2026-11-12",
        },
        "alternativa_citada_nao_usada": {
            "id": QWEN_ALT,
            "licenca_card": "Apache-2.0",
            "nota": "tokenizer diferente do aluno; logits KD exigiria o mesmo vocabulário. O lab usa SmolLM2-360M.",
            "card": "https://huggingface.co/Qwen/Qwen2.5-0.5B",
        },
        "dados_sinteticos": (
            "compleções do professor herdam a licença Apache-2.0 do modelo. "
            "API comercial (OpenAI etc.) costuma proibir treinar aluno — não é o caso aqui."
        ),
        "mesmo_tokenizer": True,
    }
