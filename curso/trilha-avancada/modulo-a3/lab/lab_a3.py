#!/usr/bin/env python3
"""Labs A3 → ``modulo-a3/saidas/ca3.json``."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a2" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from acumulo import grads_acumulo_vs_batch, treinar_passos  # noqa: E402
from mini_decoder import MiniCfg, MiniDecoder, ce_proximo_token  # noqa: E402
from versoes import coletar_bancada, orcamento_memoria, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca3.json"


def main() -> None:
    t0 = time.perf_counter()
    print("=== A3.1 MiniDecoder + CE com shift ===")
    tr = treinar_passos(40)
    print(
        f"  n_params={tr['n_params']} loss {tr['loss_ini']:.4f} → {tr['loss_fim']:.4f} "
        f"acc={tr['acuracia_proximo']:.3f} caiu={tr['caiu']}"
    )
    print("=== A3.2 accumulation vs batch (dropout off) ===")
    ac = grads_acumulo_vs_batch()
    print(f"  delta_max={ac['delta_max']:.3e} passou={ac['passou']}")
    print("=== A3.3 envelope vs RSS ===")
    m = MiniDecoder(MiniCfg())
    orc = orcamento_memoria(m.n_params(), 4)
    rss = rss_mb()
    payload = {
        "ambiente": coletar_bancada(),
        "honestidade": {
            "tinystories": "nao_baixado; corpus sintético (contador mod V)",
            "minigpt_llm_course": "apontado, não copiado",
            "t4": "nao_calibrado",
        },
        "a3_1": tr,
        "a3_2": ac,
        "a3_3": {
            "orcamento": orc,
            "rss_processo_mb": rss,
            "nota": "modelo ~50k params; RSS é o processo Python, não o envelope do 135M",
        },
        "a3_4_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")
    _ = ce_proximo_token  # noqa: silêncio se unused lint


if __name__ == "__main__":
    main()
