"""DPO (e família) com TRL + LoRA em SmolLM2. Poucos passos, CPU.

A5/A6 ausentes: partimos do base, não de um SFT da trilha. T4/Colab: ver README.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset

MODELO = "HuggingFaceTB/SmolLM2-135M"
SAIDA_TREINO = Path(__file__).resolve().parent.parent / "saidas" / "runs"


def _peft():
    from peft import LoraConfig

    return LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM", target_modules=["q_proj", "v_proj"])


def _tok():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok


def treinar_dpo(
    pares: list[dict[str, str]],
    *,
    max_steps: int | None = None,
    beta: float = 0.1,
    loss_type: str = "sigmoid",
    output_dir: str | Path | None = None,
    lr: float = 2e-4,
) -> dict[str, Any]:
    from trl import DPOConfig, DPOTrainer

    max_steps = max_steps if max_steps is not None else int(os.environ.get("TRILHA_A8_PASSOS", "8"))
    output_dir = Path(output_dir or (SAIDA_TREINO / f"dpo-{loss_type}"))
    output_dir.mkdir(parents=True, exist_ok=True)
    tok = _tok()
    ds = Dataset.from_list(pares)
    eval_ds = ds
    args = DPOConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        max_steps=max_steps,
        learning_rate=lr,
        beta=beta,
        loss_type=loss_type,
        max_length=128,
        logging_steps=1,
        eval_strategy="steps",
        eval_steps=max(max_steps, 1),
        save_strategy="no",
        report_to=[],
        fp16=False,
        bf16=False,
        gradient_checkpointing=False,
        remove_unused_columns=False,
        seed=0,
        warmup_steps=0,
        dataloader_pin_memory=False,
    )
    trainer = DPOTrainer(
        model=MODELO,
        args=args,
        train_dataset=ds,
        eval_dataset=eval_ds,
        processing_class=tok,
        peft_config=_peft(),
    )
    train = trainer.train()
    logs = [m for m in trainer.state.log_history if isinstance(m, dict)]
    accs = [m["rewards/accuracies"] for m in logs if "rewards/accuracies" in m]
    eval_m = trainer.evaluate()
    # modelo treinado (peft) para logps
    return {
        "loss_type": loss_type,
        "beta": beta,
        "max_steps": max_steps,
        "train_loss": float(train.training_loss) if train.training_loss is not None else None,
        "eval": {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in eval_m.items()},
        "rewards_accuracies_log": accs,
        "log_history": logs,
        "api": "trl.DPOTrainer (estavel)",
        "trainer": trainer,
        "tokenizer": tok,
    }


def tentar_experimental(pares: list[dict[str, str]], *, max_steps: int = 1) -> dict[str, Any]:
    """ORPO e SimPO (CPO) vivem em ``trl.experimental``. 1 passo ou erro documentado."""
    out: dict[str, Any] = {}
    tok = _tok()
    ds = Dataset.from_list(pares)
    try:
        from trl.experimental.orpo import ORPOConfig, ORPOTrainer

        cfg = ORPOConfig(
            output_dir=str(SAIDA_TREINO / "orpo"),
            per_device_train_batch_size=1,
            max_steps=max_steps,
            learning_rate=2e-4,
            max_length=128,
            logging_steps=1,
            save_strategy="no",
            report_to=[],
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
            seed=0,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
        tr = ORPOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
        r = tr.train()
        out["orpo"] = {
            "status": "ok",
            "api": "trl.experimental.orpo.ORPOTrainer",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
        }
        del tr
    except Exception as e:
        out["orpo"] = {"status": "falhou", "api": "trl.experimental.orpo.ORPOTrainer", "erro": f"{type(e).__name__}: {e}"}

    try:
        from trl.experimental.cpo import CPOConfig, CPOTrainer

        cfg = CPOConfig(
            output_dir=str(SAIDA_TREINO / "simpo"),
            per_device_train_batch_size=1,
            max_steps=max_steps,
            learning_rate=2e-4,
            max_length=128,
            loss_type="simpo",
            logging_steps=1,
            save_strategy="no",
            report_to=[],
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
            seed=0,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
        tr = CPOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
        r = tr.train()
        out["simpo"] = {
            "status": "ok",
            "api": "trl.experimental.cpo.CPOTrainer loss_type=simpo",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
        }
        del tr
    except Exception as e:
        out["simpo"] = {
            "status": "falhou",
            "api": "trl.experimental.cpo.CPOTrainer loss_type=simpo",
            "erro": f"{type(e).__name__}: {e}",
        }
    return out


def tentar_kto(pares_kto: list[dict], *, max_steps: int = 2) -> dict[str, Any]:
    try:
        from trl import KTOConfig, KTOTrainer

        tok = _tok()
        ds = Dataset.from_list(pares_kto)
        cfg = KTOConfig(
            output_dir=str(SAIDA_TREINO / "kto"),
            per_device_train_batch_size=2,
            max_steps=max_steps,
            learning_rate=2e-4,
            max_length=128,
            logging_steps=1,
            save_strategy="no",
            report_to=[],
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
            seed=0,
            dataloader_pin_memory=False,
        )
        tr = KTOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
        r = tr.train()
        return {
            "status": "ok",
            "api": "trl.KTOTrainer (estavel)",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
        }
    except Exception as e:
        return {"status": "falhou", "api": "trl.KTOTrainer (estavel)", "erro": f"{type(e).__name__}: {e}"}
