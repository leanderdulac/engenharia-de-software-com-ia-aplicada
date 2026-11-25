#!/usr/bin/env python3
"""Labs A6 → ``modulo-a6/saidas/ca6.json``."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a5" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a4" / "lab"))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from alvos_lora import tabela_params  # noqa: E402
from gguf_status import status as gguf  # noqa: E402
from merge_lora import delta_merge  # noqa: E402
from multi_adapter import comparar  # noqa: E402
from versoes import coletar_bancada, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca6.json"


def main() -> None:
    t0 = time.perf_counter()
    print("=== A6.1 alvos LoRA (params) ===")
    tab = tabela_params()
    for r in tab:
        print(f"  {r['nome']:12} n_treino={r['n_treino']:,}  frac={r['fracao']:.4f}")

    print("=== A6.2 merge π_SFT vs adapter ===")
    mg = delta_merge()
    print(f"  status={mg['status']} delta_max={mg.get('delta_max')} passou={mg.get('passou')}")

    print("=== A6.3 multi-adapter Amplitude + soma ===")
    t3 = time.perf_counter()
    duo = comparar()
    print(
        f"  status={duo.get('status')} json_ok={duo.get('amplitude_json_ok')} "
        f"soma_4={duo.get('soma_comeca_4')} ({time.perf_counter()-t3:.1f}s)"
    )

    print("=== A6.4 GGUF / Ollama ===")
    g = gguf()
    print(f"  {g}")

    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "honestidade": {
            "llm_course_m06": "apontado, nao copiado",
            "gguf_ollama": "nao_calibrado",
            "t4": "nao_calibrado",
            "pi_sft": "merge e multi-adapter partem do adapter A5",
        },
        "a6_1": tab,
        "a6_2": mg,
        "a6_3": {
            k: v
            for k, v in duo.items()
            if k
            in (
                "status",
                "loss_soma",
                "amplitude_json_ok",
                "soma_comeca_4",
                "amplitude_no_json",
                "soma_no_json",
                "amplitude_em_2mais2",
                "soma_em_2mais2",
            )
        },
        "a6_4": g,
        "a6_5_t4": {"status": "nao_calibrado"},
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
