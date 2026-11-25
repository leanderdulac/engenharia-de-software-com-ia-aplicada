#!/usr/bin/env python3
"""Labs A4 → ``modulo-a4/saidas/ca4.json``."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from dialogos_amplitude import SYSTEM, dialogos_eval, dialogos_treino, split_ok  # noqa: E402
from mascarar_sft import colar, lote, resumo, tensorizar_turnos  # noqa: E402
from versoes import coletar_bancada, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca4.json"
MODELO = os.environ.get("TRILHA_A4_MODELO", "HuggingFaceTB/SmolLM2-135M")


def main() -> None:
    from transformers import AutoTokenizer

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tpl = getattr(tok, "chat_template", None)

    print("=== A4.1 tokenizer + template declarado ===")
    print(f"  modelo={MODELO} chat_template={'ausente' if not tpl else 'presente'}")

    print("=== A4.2 treino/eval com e sem system ===")
    tr_sys = lote(tok, dialogos_treino(), system=SYSTEM)
    tr_nos = lote(tok, dialogos_treino(), system=None)
    ev_sys = lote(tok, dialogos_eval(), system=SYSTEM)
    r_tr_sys, r_tr_nos, r_ev = resumo(tr_sys), resumo(tr_nos), resumo(ev_sys)
    delta_prompt = r_tr_sys["n_prompt_medio"] - r_tr_nos["n_prompt_medio"]
    print(
        f"  treino+sys n_prompt={r_tr_sys['n_prompt_medio']} "
        f"n_asst={r_tr_sys['n_assistant_medio']} frac_prompt={r_tr_sys['fracao_prompt_media']}"
    )
    print(f"  sem system n_prompt={r_tr_nos['n_prompt_medio']}  Δprompt={delta_prompt:.2f} tok")
    print(f"  eval n={r_ev['n']} split_ok={split_ok()} todos_eos={r_tr_sys['todos_eos']}")

    print("=== A4.3 multi-turn (só assistant na loss) ===")
    mt = tensorizar_turnos(
        tok,
        [
            ("user", "Placa ABC-1D23. Segurado?"),
            ("assistant", "Ana Souza."),
            ("user", "Valor?"),
            ("assistant", "1250.00"),
        ],
        system=SYSTEM,
    )
    print(f"  n_total={mt['n_total']} n_assistant={mt['n_assistant']} n_prompt={mt['n_prompt']}")

    print("=== A4.4 padding / truncamento ===")
    pad = colar(tr_sys, tok.pad_token_id)
    trunc = colar(tr_sys, tok.pad_token_id, max_len=48)
    print(
        f"  pad L={pad['L']} truncou={pad['truncou']} | "
        f"max_len=48 L={trunc['L']} truncou={trunc['truncou']} "
        f"asst {trunc['n_assistant_medio_antes']:.1f}→{trunc['n_assistant_medio_depois']:.1f}"
    )

    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "honestidade": {
            "jsonl_m09": "nao_lido; dialogos originais no espirito Amplitude",
            "oasst1": "nao_baixado",
            "instruct_05b": "nao_baixado; SmolLM2-135M base, template declarado no lab",
            "t4": "nao_calibrado",
            "efeito_system_no_sft": "A5 mede acuracia; aqui so n_tokens",
        },
        "a4_1": {
            "modelo": MODELO,
            "chat_template_no_tokenizer": bool(tpl),
            "template": "### system / ### user / ### assistant (ASCII, desta trilha)",
            "eos_token": tok.eos_token,
        },
        "a4_2": {
            "split_ok": split_ok(),
            "treino_com_system": r_tr_sys,
            "treino_sem_system": r_tr_nos,
            "eval_com_system": r_ev,
            "delta_n_prompt_system": round(delta_prompt, 2),
            "exemplo_n_prompt": tr_sys[0]["n_prompt"],
            "exemplo_n_total": tr_sys[0]["n_total"],
            "exemplo_labels_head": tr_sys[0]["labels"][:8],
            "exemplo_labels_tail": tr_sys[0]["labels"][-8:],
        },
        "a4_3": {
            "n_total": mt["n_total"],
            "n_assistant": mt["n_assistant"],
            "n_prompt": mt["n_prompt"],
            "so_assistant_na_loss": mt["n_assistant"] < mt["n_total"],
        },
        "a4_4": {
            "pad": {k: pad[k] for k in ("L", "truncou", "n_assistant_medio_depois")},
            "trunc_48": {
                "L": trunc["L"],
                "truncou": trunc["truncou"],
                "n_assistant_antes": trunc["n_assistant_medio_antes"],
                "n_assistant_depois": trunc["n_assistant_medio_depois"],
            },
        },
        "a4_5_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
