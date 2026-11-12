"""Versões pinadas da bancada — o que está instalado, não o que o cartaz promete."""

from __future__ import annotations

import importlib
import os
import platform
import time
from typing import Any

PACOTES = (
    "torch",
    "transformers",
    "accelerate",
    "safetensors",
    "peft",
    "trl",
    "datasets",
    "bitsandbytes",
)


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def versao(mod: str) -> str | None:
    try:
        m = importlib.import_module(mod)
    except ImportError:
        return None
    return getattr(m, "__version__", "sem_version")


def rss_mb() -> float | None:
    try:
        with open("/proc/self/status", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024, 1)
    except OSError:
        return None
    return None


def coletar_bancada() -> dict[str, Any]:
    import torch

    gpu = None
    if torch.cuda.is_available():
        gpu = {
            "nome": torch.cuda.get_device_name(0),
            "memoria_total_gb": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
        }
    pkgs = {p: versao(p) for p in PACOTES}
    return {
        "python": platform.python_version(),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "gpu": gpu,
        "cpu": _cpu_model(),
        "cpus_logicas": os.cpu_count(),
        "plataforma": platform.platform(),
        "epoch_unix": int(time.time()),
        "pacotes": pkgs,
        "bitsandbytes_cpu": pkgs["bitsandbytes"] is not None,
        "rss_inicio_mb": rss_mb(),
    }


def orcamento_memoria(n_params: int, dtype_bytes: int = 4) -> dict[str, Any]:
    """Conta de envelope (pôster M09): pesos + grad + Adam (m,v). Sem ativações."""
    pesos = n_params * dtype_bytes
    grad = n_params * dtype_bytes
    adam = 2 * n_params * 4  # estados fp32
    total = pesos + grad + adam
    return {
        "n_params": n_params,
        "dtype_bytes": dtype_bytes,
        "pesos_mb": round(pesos / 1e6, 1),
        "grad_mb": round(grad / 1e6, 1),
        "adam_mb": round(adam / 1e6, 1),
        "total_treino_mb": round(total / 1e6, 1),
        "nota": "sem ativações nem KV; T4 = nao_calibrado nesta CPU",
    }
