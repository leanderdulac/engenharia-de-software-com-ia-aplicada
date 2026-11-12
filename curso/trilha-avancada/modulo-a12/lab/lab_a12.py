#!/usr/bin/env python3
"""Labs A12 → ``modulo-a12/saidas/ca12.json``."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
for extra in ("modulo-a8/lab", "modulo-a11/lab", "modulo-a5/lab", "modulo-a0/lab"):
    sys.path.insert(0, str(AQUI.parents[1] / extra))

from duas_tecnicas import tecnica_preferencia, tecnica_ptq  # noqa: E402
from versoes import coletar_bancada, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca12.json"
ADR = AQUI.parent / "adr-capstone.md"


def main() -> None:
    t0 = time.perf_counter()
    print("=== A12.1 técnica A8: preferência implícita base vs π_SFT ===")
    pref = tecnica_preferencia()
    print(
        f"  n={pref['base']['n']} bruta_base={pref['base']['preferencia_bruta']:.3f} "
        f"bruta_sft={pref['pi_sft']['preferencia_bruta']:.3f} melhorou={pref['melhorou']}"
    )
    print("=== A12.2 técnica A11: PTQ INT8 vs fp32 ===")
    ptq = tecnica_ptq()
    print(
        f"  ppl_fp32={ptq['ppl_fp32']:.3f} ppl_int8={ptq['ppl_int8']:.3f} "
        f"delta={ptq['delta_ppl']:.3f} piorou={ptq['int8_piorou']}"
    )
    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "honestidade": {
            "c09_5": "apontado; ADR desta trilha e original (nao copia decisoes-de-arquitetura.md)",
            "dpo_grpo_destilacao_retreino": "nao_reexecutado; A8 entra como logps, A11 como PTQ",
            "t4": "nao_calibrado",
            "ic95": "nao_calibrado",
            "harness_amplitude_m09": "nao_lido",
        },
        "tecnicas": ["A8-logps", "A11-ptq-int8"],
        "a12_1": pref,
        "a12_2": ptq,
        "a12_3_adr": {"arquivo": "adr-capstone.md", "existe": ADR.is_file()},
        "a12_4_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
