"""Ponto de partida π_SFT para A8/A9/A10.

``TRILHA_PI_SFT=0`` desliga. ``TRILHA_PI_SFT=/caminho`` força um adapter.
Sem env, usa ``modulo-a5/execucao/pi_sft/`` se houver ``adapter_config.json``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

MODELO = "HuggingFaceTB/SmolLM2-135M"
PI_SFT_PADRAO = Path(__file__).resolve().parents[1] / "execucao" / "pi_sft"


def resolver(caminho: str | Path | None = None) -> Path | None:
    env = os.environ.get("TRILHA_PI_SFT") if caminho is None else str(caminho)
    if caminho is None and env in ("0", "false", "nao", "off"):
        return None
    if caminho is None and env not in (None, "", "1", "true", "sim", "on"):
        p = Path(env)
    elif caminho is not None:
        p = Path(caminho)
    else:
        p = PI_SFT_PADRAO
    if (p / "adapter_config.json").is_file():
        return p
    return None


def manifesto(caminho: str | Path | None = None) -> dict[str, Any]:
    p = resolver(caminho)
    return {
        "encontrado": p is not None,
        "caminho": str(p) if p else None,
        "env": os.environ.get("TRILHA_PI_SFT"),
        "padrao": str(PI_SFT_PADRAO),
        "ponto_partida": "pi_sft" if p else "smollm2_base",
    }


def carregar_base_ou_sft(
    modelo_id: str = MODELO,
    *,
    merge: bool = True,
    device: str = "cpu",
    caminho: str | Path | None = None,
):
    """Devolve ``(modelo, tokenizer, manifesto)``. Merge o LoRA no base se houver π_SFT."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(modelo_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    m = AutoModelForCausalLM.from_pretrained(modelo_id, dtype=torch.float32)
    info = manifesto(caminho)
    p = resolver(caminho)
    if p is not None:
        from peft import PeftModel

        m = PeftModel.from_pretrained(m, str(p))
        if merge:
            m = m.merge_and_unload()
    m.to(device)
    return m, tok, info
