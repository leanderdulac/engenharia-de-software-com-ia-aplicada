#!/usr/bin/env python3
"""Labs A7 → ``modulo-a7/saidas/ca7.json``."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a5" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a4" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from aritmetica import split_ok, voto  # noqa: E402
from gerar_raciocinio import avaliar  # noqa: E402
from versoes import coletar_bancada, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca7.json"


def main() -> None:
    t0 = time.perf_counter()
    n_eval = int(os.environ.get("TRILHA_A7_N", "8"))
    n_sc = int(os.environ.get("TRILHA_A7_SC", "4"))
    print("=== A7.1 direto vs CoT vs self-consistency ===")
    r = avaliar(n_eval=n_eval, n_sc=n_sc)
    print(
        f"  n={r['n']} acc_dir={r['acc_direto']:.3f} acc_cot={r['acc_cot']:.3f} "
        f"acc_sc={r['acc_sc']:.3f} cot_piorou={r['cot_piorou']} "
        f"motivo_errado={r['taxa_certo_motivo_errado']:.3f}"
    )
    demo = voto(["Resposta: 7", "acho que 7", "Resposta: 9", "7"])
    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "honestidade": {
            "gsm8k": "nao_baixado; somas curtas originais",
            "m04_react": "apontado, nao copiado; aqui raciocinio e dado, nao agente",
            "t4": "nao_calibrado",
            "ic95": "nao_calibrado (n=8, 1 semente)",
            "pi_sft": "nao usado; base SmolLM2-135M (SFT A5 e JSON, nao CoT)",
        },
        "a7_1": {k: v for k, v in r.items() if k != "linhas"},
        "a7_1_amostra": r["linhas"][:3],
        "a7_2": {"voto_demo": demo, "split_ok": split_ok()},
        "a7_3_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
