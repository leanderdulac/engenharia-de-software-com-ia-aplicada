#!/usr/bin/env python3
"""Lab A0 → ``modulo-a0/saidas/ca0.json`` (bancada.json no mesmo objeto).

    python modulo-a0/lab/lab_a0.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from bancada_latencia import PROMPTS, gerar_lote, p50_dentro_de  # noqa: E402
from versoes import coletar_bancada, orcamento_memoria, rss_mb  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca0.json"
MODELO = os.environ.get("TRILHA_A0_MODELO", "HuggingFaceTB/SmolLM2-135M")
N = int(os.environ.get("TRILHA_A0_N", "20"))
SEMENTE = int(os.environ.get("TRILHA_A0_SEMENTE", "0"))


def main() -> None:
    t0 = time.perf_counter()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    bancada = coletar_bancada()
    bancada["modelo"] = MODELO
    bancada["semente"] = SEMENTE
    print(f"=== A0.1 bancada {MODELO} n={N} seed={SEMENTE} ===")
    print(f"  device={bancada['device']} gpu={bancada['gpu']}")
    print(f"  torch={bancada['pacotes']['torch']} transformers={bancada['pacotes']['transformers']}")

    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    model.to("cpu")
    n_params = int(model.num_parameters())
    orc = orcamento_memoria(n_params, 4)
    prompts = (PROMPTS * ((N + len(PROMPTS) - 1) // len(PROMPTS)))[:N]

    c1 = gerar_lote(model, tok, prompts, semente=SEMENTE)
    print(
        f"  corrida1 p50={c1['latencia_p50_s']:.3f}s p95={c1['latencia_p95_s']:.3f}s "
        f"tok/s={c1['tokens_por_s']:.2f} rss_pico={c1['rss_pico_mb']}"
    )
    c2 = gerar_lote(model, tok, prompts, semente=SEMENTE)
    ok = p50_dentro_de(c1["latencia_p50_s"], c2["latencia_p50_s"])
    print(f"  corrida2 p50={c2['latencia_p50_s']:.3f}s  repetivel_p50_±20%={ok}")

    payload = {
        "ambiente": bancada,
        "honestidade": {
            "instruct_05b": (
                "plano pedia instruct ~0,5B; nesta CPU usamos SmolLM2-135M já no cache da trilha. "
                "Qwen2.5-0.5B = nao_baixado (opcional TRILHA_A0_MODELO)."
            ),
            "t4_colab": "nao_calibrado",
            "trackio": "nao_instalado; o registro é este JSON",
        },
        "a0_1": {
            "modelo": MODELO,
            "n_params": n_params,
            "n_prompts": N,
            "semente": SEMENTE,
            "corrida1": {k: v for k, v in c1.items() if k != "latencias_s"},
            "corrida2": {k: v for k, v in c2.items() if k != "latencias_s"},
            "p50_repetivel_20pct": ok,
            "orcamento": orc,
            "rss_fim_mb": rss_mb(),
        },
        "a0_2_t4": {
            "status": "nao_calibrado",
            "motivo": "CPU sem CUDA; envelope T4 fica para Colab",
        },
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
