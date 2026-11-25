"""Coleta Python, torch, CPU/GPU — para o JSON do checkpoint, sem inventar número."""

from __future__ import annotations

import os
import platform
import time
from typing import Any


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def coletar_ambiente() -> dict[str, Any]:
    import torch
    import transformers

    gpu = None
    if torch.cuda.is_available():
        gpu = {
            "nome": torch.cuda.get_device_name(0),
            "memoria_total_gb": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
        }
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "gpu": gpu,
        "cpu": _cpu_model(),
        "cpus_logicas": os.cpu_count(),
        "plataforma": platform.platform(),
        "epoch_unix": int(time.time()),
    }
