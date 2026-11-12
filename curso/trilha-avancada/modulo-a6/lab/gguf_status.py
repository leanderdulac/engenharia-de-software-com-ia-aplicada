"""GGUF / Ollama / llama.cpp — nesta CPU, só o status."""

from __future__ import annotations

import importlib.util
import shutil
from typing import Any


def status() -> dict[str, Any]:
    llama = importlib.util.find_spec("llama_cpp") is not None
    ollama = shutil.which("ollama")
    return {
        "status": "nao_calibrado",
        "llama_cpp": llama,
        "ollama": ollama,
        "nota": "sem export GGUF nem serve Ollama nesta bancada; A11 já cobre PTQ INT8/INT4",
    }
