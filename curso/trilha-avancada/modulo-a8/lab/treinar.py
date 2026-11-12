"""DPO (e família) com TRL + LoRA em SmolLM2. Poucos passos, CPU.

A5/A6 ausentes: partimos do base, não de um SFT da trilha. T4/Colab: ver README.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import torch
from datasets import Dataset

_AVISO_PREFIXO = "not a prefix of the tokenized prompt+completion"


class _CapturaLog(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.msgs: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        self.msgs.append(record.getMessage())


@contextmanager
def capturar_logs_trl() -> Iterator[list[str]]:
    buf = _CapturaLog()
    buf.setLevel(logging.WARNING)
    nomes = (
        "trl",
        "trl.trainer.dpo_trainer",
        "trl.trainer.kto_trainer",
        "trl.experimental.orpo",
        "trl.experimental.cpo",
    )
    logs = [logging.getLogger(n) for n in nomes]
    for log in logs:
        log.addHandler(buf)
    try:
        yield buf.msgs
    finally:
        for log in logs:
            log.removeHandler(buf)


def resumo_aviso_prefixo(msgs: list[str]) -> dict[str, Any]:
    hits = [m for m in msgs if _AVISO_PREFIXO in m]
    return {"ocorreu": bool(hits), "n": len(hits), "amostra": hits[:2]}

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
    pares_treino: list[dict[str, str]],
    *,
    pares_eval: list[dict[str, str]] | None = None,
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
    ds = Dataset.from_list(pares_treino)
    eval_ds = Dataset.from_list(pares_eval) if pares_eval else None
    tem_eval = eval_ds is not None and len(pares_eval or []) > 0
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
        eval_strategy="steps" if tem_eval else "no",
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
    with capturar_logs_trl() as msgs:
        trainer = DPOTrainer(
            model=MODELO,
            args=args,
            train_dataset=ds,
            eval_dataset=eval_ds,
            processing_class=tok,
            peft_config=_peft(),
        )
        train = trainer.train()
        eval_m = trainer.evaluate() if tem_eval else {}
    aviso = resumo_aviso_prefixo(msgs)
    logs = [m for m in trainer.state.log_history if isinstance(m, dict)]
    accs = [m["rewards/accuracies"] for m in logs if "rewards/accuracies" in m]
    return {
        "loss_type": loss_type,
        "beta": beta,
        "max_steps": max_steps,
        "n_treino": len(pares_treino),
        "n_eval": len(pares_eval or []),
        "train_loss": float(train.training_loss) if train.training_loss is not None else None,
        "eval": {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in eval_m.items()},
        "rewards_accuracies_log": accs,
        "log_history": logs,
        "aviso_prefixo_trl": aviso,
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
        with capturar_logs_trl() as msgs:
            tr = ORPOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
            r = tr.train()
        out["orpo"] = {
            "status": "ok",
            "api": "trl.experimental.orpo.ORPOTrainer",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
            "aviso_prefixo_trl": resumo_aviso_prefixo(msgs),
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
        with capturar_logs_trl() as msgs:
            tr = CPOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
            r = tr.train()
        out["simpo"] = {
            "status": "ok",
            "api": "trl.experimental.cpo.CPOTrainer loss_type=simpo",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
            "aviso_prefixo_trl": resumo_aviso_prefixo(msgs),
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
        with capturar_logs_trl() as msgs:
            tr = KTOTrainer(model=MODELO, args=cfg, train_dataset=ds, processing_class=tok, peft_config=_peft())
            r = tr.train()
        return {
            "status": "ok",
            "api": "trl.KTOTrainer (estavel)",
            "train_loss": float(r.training_loss) if r.training_loss is not None else None,
            "max_steps": max_steps,
            "aviso_prefixo_trl": resumo_aviso_prefixo(msgs),
        }
    except Exception as e:
        return {"status": "falhou", "api": "trl.KTOTrainer (estavel)", "erro": f"{type(e).__name__}: {e}"}
