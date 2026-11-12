#!/usr/bin/env python3
"""Labs A5 → ``modulo-a5/saidas/ca5.json`` + adapter ``execucao/pi_sft/``."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a4" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from dialogos_amplitude import SYSTEM, dialogos_eval, dialogos_treino  # noqa: E402
from mascarar_sft import lote  # noqa: E402
from pi_sft import MODELO, PI_SFT_PADRAO, manifesto  # noqa: E402
from sft_lora import (  # noqa: E402
    avaliar_dialogos,
    probes_geral,
    tokenizer,
    treinar_sft,
)
from versoes import coletar_bancada, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca5.json"


def _sem_model(d: dict) -> dict:
    return {k: v for k, v in d.items() if k not in {"model", "tokenizer", "historico", "linhas"}}


def main() -> None:
    t0 = time.perf_counter()
    passos = int(os.environ.get("TRILHA_A5_PASSOS", "64"))
    tok = tokenizer()
    tr_itens = lote(tok, dialogos_treino(), system=SYSTEM)
    print("=== A5.0 probes no base (antes do SFT) ===")
    import torch
    from transformers import AutoModelForCausalLM

    base = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    base.eval()
    probes_antes = probes_geral(base, tok)
    for k, v in probes_antes.items():
        print(f"  base {k!r} → {v!r}")
    del base
    print("=== A5.1 SFT assistant-only (π_SFT) ===")
    sft = treinar_sft(tr_itens, passos=passos, so_assistant=True, salvar_em=PI_SFT_PADRAO)
    model, tok_m = sft["model"], sft["tokenizer"]
    print(
        f"  loss {sft['loss_ini']:.4f} → {sft['loss_fim']:.4f} "
        f"fracao_treino={sft['fracao_treino']:.4f} salvo={sft['salvo_em']}"
    )

    print("=== A5.2 eval Amplitude (treino vs hold-out) ===")
    ev_tr = avaliar_dialogos(model, tok_m, dialogos_treino(), system=SYSTEM)
    ev_ev = avaliar_dialogos(model, tok_m, dialogos_eval(), system=SYSTEM)
    print(f"  treino acc={ev_tr['acuracia']:.3f}  eval acc={ev_ev['acuracia']:.3f}")

    print("=== A5.3 probes gerais (esquecimento, sem GSM8K/Dolly) ===")
    geral = probes_geral(model, tok_m)
    for k, v in geral.items():
        print(f"  {k!r} → {v!r}")
    del model, tok_m, sft["model"], sft["tokenizer"]

    print("=== A5.4 SFT prompt+resposta (mesmo n passos, não salva) ===")
    full = treinar_sft(tr_itens, passos=min(passos, 8), so_assistant=False, seed=1, salvar_em=None)
    ev_full = avaliar_dialogos(full["model"], full["tokenizer"], dialogos_eval(), system=SYSTEM)
    print(f"  full loss {full['loss_ini']:.4f} → {full['loss_fim']:.4f} eval acc={ev_full['acuracia']:.3f}")
    del full["model"]

    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "honestidade": {
            "gsm8k_dolly": "nao_baixado; probes 2+2 e capital of France",
            "jsonl_m09": "nao_lido; dialogos A4",
            "wandb": "nao_usado; tracking no JSON",
            "t4": "nao_calibrado",
            "tres_sementes_harness": "nao_calibrado",
            "pi_sft": manifesto(),
        },
        "a5_1": {**_sem_model(sft), "historico_tail": sft["historico"][-5:]},
        "a5_2": {
            "treino": {"n": ev_tr["n"], "n_ok": ev_tr["n_ok"], "acuracia": ev_tr["acuracia"]},
            "eval": {"n": ev_ev["n"], "n_ok": ev_ev["n_ok"], "acuracia": ev_ev["acuracia"]},
            "amostra_eval": ev_ev["linhas"],
        },
        "a5_3": {
            "antes": probes_antes,
            "depois": geral,
            "nota": "qualitativo; sem dataset geral publico; n=2 probes",
        },
        "a5_4": {
            "full": _sem_model(full),
            "eval_acuracia": ev_full["acuracia"],
            "assistant_eval_acuracia": ev_ev["acuracia"],
        },
        "a5_5_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")
    print(f"π_SFT → {PI_SFT_PADRAO}")


if __name__ == "__main__":
    main()
