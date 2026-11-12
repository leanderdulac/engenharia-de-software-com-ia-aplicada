"""GRPOTrainer do TRL que atualiza pesos (LoRA) — não o demo do M09."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

os.environ.setdefault("WANDB_DISABLED", "true")

import torch
from datasets import Dataset

MODELO = "HuggingFaceTB/SmolLM2-135M"
SAIDA = Path(__file__).resolve().parent.parent / "saidas" / "runs"


def _peft():
    from peft import LoraConfig

    return LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )


def _tok():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok


def _kl_de_logs(logs: list[dict]) -> list[float]:
    out: list[float] = []
    for m in logs:
        for k, v in m.items():
            if not isinstance(v, (int, float)):
                continue
            kl = k == "kl" or k.endswith("/kl") or k.endswith("_kl")
            if kl:
                out.append(float(v))
    return out


def _compactar_logs(logs: list[dict]) -> list[dict]:
    keep = (
        "step",
        "loss",
        "grad_norm",
        "reward",
        "reward_std",
        "frac_reward_zero_std",
        "kl",
        "entropy",
    )
    out = []
    for m in logs:
        if not any(k in m for k in ("reward", "kl", "train_loss")):
            continue
        row = {k: m[k] for k in keep if k in m}
        for k, v in m.items():
            if k not in row and "kl" in k.lower() and isinstance(v, (int, float)):
                row[k] = v
        if row:
            out.append(row)
    return out


@torch.no_grad()
def gerar_e_pontuar(
    model,
    tok,
    pares: list[dict],
    reward_fn: Callable,
    *,
    max_novos: int = 8,
    device: str = "cpu",
    batch_size: int = 8,
    n_amostra: int = 8,
) -> dict[str, Any]:
    model.eval()
    lado = getattr(tok, "padding_side", "right")
    tok.padding_side = "left"
    comps: list[str] = []
    try:
        for i in range(0, len(pares), batch_size):
            chunk = pares[i : i + batch_size]
            enc = tok([p["prompt"] for p in chunk], return_tensors="pt", padding=True)
            enc = {k: v.to(device) for k, v in enc.items()}
            in_len = enc["input_ids"].shape[1]
            out = model.generate(
                **enc,
                max_new_tokens=max_novos,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
            for row in out:
                comps.append(tok.decode(row[in_len:], skip_special_tokens=True))
    finally:
        tok.padding_side = lado
    answers = [p["answer"] for p in pares]
    rs = reward_fn(comps, answer=answers)
    amostra = [
        {"prompt": p["prompt"].strip(), "ouro": p["answer"], "gerado": c, "r": r}
        for p, c, r in zip(pares[:n_amostra], comps[:n_amostra], rs[:n_amostra])
    ]
    return {
        "n": len(pares),
        "recompensa_media": float(sum(rs) / max(len(rs), 1)),
        "n_acertos": int(sum(1 for r in rs if r >= 1.0)),
        "amostra": amostra,
    }


def treinar_grpo(
    pares: list[dict],
    reward_fn: Callable,
    *,
    beta: float = 0.0,
    max_steps: int | None = None,
    num_generations: int | None = None,
    max_completion_length: int = 8,
    output_dir: str | Path | None = None,
    lr: float = 2e-4,
    seed: int = 0,
    temperature: float = 1.0,
    devolver_trainer: bool = True,
) -> dict[str, Any]:
    from trl import GRPOConfig, GRPOTrainer

    max_steps = max_steps if max_steps is not None else int(os.environ.get("TRILHA_A9_PASSOS", "16"))
    num_generations = num_generations if num_generations is not None else int(os.environ.get("TRILHA_A9_G", "4"))
    output_dir = Path(output_dir or (SAIDA / f"grpo-b{beta}-s{seed}"))
    output_dir.mkdir(parents=True, exist_ok=True)
    tok = _tok()
    colunas = [{"prompt": p["prompt"], "answer": p["answer"]} for p in pares]
    ds = Dataset.from_list(colunas)
    args = GRPOConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=num_generations,
        generation_batch_size=num_generations,
        num_generations=num_generations,
        max_completion_length=max_completion_length,
        max_steps=max_steps,
        learning_rate=lr,
        beta=beta,
        logging_steps=1,
        save_strategy="no",
        report_to=[],
        fp16=False,
        bf16=False,
        use_cpu=True,
        gradient_checkpointing=False,
        seed=seed,
        data_seed=seed,
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        use_vllm=False,
        temperature=temperature,
    )
    trainer = GRPOTrainer(
        model=MODELO,
        reward_funcs=reward_fn,
        args=args,
        train_dataset=ds,
        processing_class=tok,
        peft_config=_peft(),
    )
    train = trainer.train()
    logs = [m for m in trainer.state.log_history if isinstance(m, dict)]
    rewards = [m.get("reward") for m in logs if "reward" in m]
    frac = [float(m["frac_reward_zero_std"]) for m in logs if "frac_reward_zero_std" in m]
    kl = _kl_de_logs(logs)
    n_zero = sum(1 for z in frac if z >= 1.0 - 1e-12)
    out = {
        "beta": beta,
        "max_steps": max_steps,
        "num_generations": num_generations,
        "temperature": temperature,
        "seed": seed,
        "train_loss": float(train.training_loss) if train.training_loss is not None else None,
        "rewards_log": [float(x) for x in rewards if x is not None],
        "kl_log": kl,
        "kl_max": max(kl) if kl else None,
        "kl_n_nao_zero": sum(1 for x in kl if abs(x) > 1e-12),
        "frac_reward_zero_std": frac,
        "n_passos_zero_std": n_zero,
        "frac_passos_zero_std": (n_zero / len(frac)) if frac else None,
        "logs_compactos": _compactar_logs(logs),
        "api": "trl.GRPOTrainer (estavel)",
        "atualiza_pesos": True,
    }
    if devolver_trainer:
        out["trainer"] = trainer
        out["tokenizer"] = tok
    else:
        del trainer
    return out
