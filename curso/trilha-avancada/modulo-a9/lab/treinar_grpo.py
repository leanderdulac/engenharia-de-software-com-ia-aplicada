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


@torch.no_grad()
def gerar_e_pontuar(
    model,
    tok,
    pares: list[dict],
    reward_fn: Callable,
    *,
    max_novos: int = 6,
    device: str = "cpu",
) -> dict[str, Any]:
    model.eval()
    comps: list[str] = []
    answers = [p["answer"] for p in pares]
    for p in pares:
        ids = tok(p["prompt"], return_tensors="pt").to(device)
        out = model.generate(
            **ids,
            max_new_tokens=max_novos,
            do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
        novo = out[0, ids["input_ids"].shape[1] :]
        comps.append(tok.decode(novo, skip_special_tokens=True))
    rs = reward_fn(comps, answer=answers)
    return {
        "n": len(pares),
        "recompensa_media": float(sum(rs) / max(len(rs), 1)),
        "n_acertos": int(sum(1 for r in rs if r >= 1.0)),
        "amostra": [{"prompt": p["prompt"].strip(), "ouro": p["answer"], "gerado": c, "r": r} for p, c, r in zip(pares, comps, rs)],
    }


def treinar_grpo(
    pares: list[dict],
    reward_fn: Callable,
    *,
    beta: float = 0.0,
    max_steps: int | None = None,
    num_generations: int = 2,
    max_completion_length: int = 6,
    output_dir: str | Path | None = None,
    lr: float = 2e-4,
) -> dict[str, Any]:
    from trl import GRPOConfig, GRPOTrainer

    max_steps = max_steps if max_steps is not None else int(os.environ.get("TRILHA_A9_PASSOS", "3"))
    output_dir = Path(output_dir or (SAIDA / f"grpo-b{beta}"))
    output_dir.mkdir(parents=True, exist_ok=True)
    tok = _tok()
    colunas = [{"prompt": p["prompt"], "answer": p["answer"]} for p in pares]
    ds = Dataset.from_list(colunas)
    args = GRPOConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=num_generations,
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
        gradient_checkpointing=False,
        seed=0,
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        use_vllm=False,
        temperature=0.8,
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
    kl = [m.get("kl") for m in logs if "kl" in m]
    return {
        "beta": beta,
        "max_steps": max_steps,
        "num_generations": num_generations,
        "train_loss": float(train.training_loss) if train.training_loss is not None else None,
        "rewards_log": [float(x) for x in rewards if x is not None],
        "kl_log": [float(x) for x in kl if x is not None],
        "log_history": logs,
        "api": "trl.GRPOTrainer (estavel)",
        "atualiza_pesos": True,
        "trainer": trainer,
        "tokenizer": tok,
    }
