"""Ablação de alvos LoRA. Conta params; treino curto opcional."""

from __future__ import annotations

from typing import Any

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

from pi_sft import MODELO

ALVOS = {
    "qv": ["q_proj", "v_proj"],
    "attn": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "mlp": ["gate_proj", "up_proj", "down_proj"],
    "all_linear": [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
}


def cfg(alvos: list[str]) -> LoraConfig:
    return LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=alvos,
    )


def contar(nome: str) -> dict[str, Any]:
    m = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    m = get_peft_model(m, cfg(ALVOS[nome]))
    n_tr = sum(p.numel() for p in m.parameters() if p.requires_grad)
    n_tot = sum(p.numel() for p in m.parameters())
    del m
    return {
        "nome": nome,
        "modulos": ALVOS[nome],
        "n_treino": n_tr,
        "n_total": n_tot,
        "fracao": n_tr / max(n_tot, 1),
    }


def tabela_params() -> list[dict[str, Any]]:
    return [contar(n) for n in ("qv", "attn", "mlp", "all_linear")]
