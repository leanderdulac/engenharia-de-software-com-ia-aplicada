#!/usr/bin/env python3
"""Roda os labs A11 e grava ``modulo-a11/saidas/ca11.json``.

Uso (em ``curso/trilha-avancada/``):

    python modulo-a11/lab/lab_a11.py

Variáveis:

    TRILHA_A11_SEM_MOE_REAL=1   não baixa Granite
    TRILHA_A11_SEM_SMOL=1       pula PTQ/KV no SmolLM2 (só brinquedo + QAT)
    TRILHA_A11_N_NOVOS=8        tokens gerados nas medições
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
A2_LAB = AQUI.parents[1] / "modulo-a2" / "lab"
sys.path.insert(0, str(A2_LAB))

from ambiente import coletar_ambiente  # noqa: E402
from inspecionar_moe import inspecionar_granite  # noqa: E402
from kv_cache import medir_cache_e_batch, prova_cache_minidecoder  # noqa: E402
from moe_brinquedo import comparar_com_sem_aux, exemplo_numerico_aula, histograma_ascii  # noqa: E402
from ptq import comparar_ptq  # noqa: E402
from qat import comparar_ptq_qat  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca11.json"


def main() -> None:
    t0 = time.perf_counter()
    payload: dict = {"ambiente": coletar_ambiente(), "honestidade": {
        "a3_a5_a6": "nao_publicados",
        "moe_brinquedo": "camada avulsa, nao MiniGPT do A3",
        "ptq": "SmolLM2-135M, nao o SFT do A5",
        "lora_moe": "CA11.3 nao executado (A6 ausente, T4 ausente); ponte conceitual: LoRA do M09",
        "t4_vllm_olmoe": "nao_calibrado",
    }}

    print("=== A11.1 MoE de brinquedo ===")
    t1 = time.perf_counter()
    ex = exemplo_numerico_aula()
    cmp_ = comparar_com_sem_aux(passos=250, semente=0)
    payload["a11_1"] = {
        "exemplo_aula": ex,
        "comparacao": {k: v for k, v in cmp_.items() if not k.startswith("hist_")},
        "histograma_sem": histograma_ascii(cmp_["sem_aux"]["f_final"]),
        "histograma_com": histograma_ascii(cmp_["com_aux"]["f_final"]),
        "segundos": round(time.perf_counter() - t1, 3),
    }
    print(payload["a11_1"]["histograma_sem"])
    print("--- com aux ---")
    print(payload["a11_1"]["histograma_com"])
    print(
        f"  f_max sem={cmp_['sem_aux']['f_max']:.3f} com={cmp_['com_aux']['f_max']:.3f}  "
        f"colapso={cmp_['colapso_sem_aux']} equilibrado={cmp_['mais_equilibrado_com_aux']}"
    )
    p = cmp_["sem_aux"]["parametros"]
    print(f"  params total={p['total']} ativos/token={p['ativos_por_token']} k={p['k']}/{p['n_experts']}")

    print("=== A11.2 Granite (ou config) ===")
    t2 = time.perf_counter()
    moe_real = inspecionar_granite()
    moe_real["segundos_lab"] = round(time.perf_counter() - t2, 3)
    payload["a11_2"] = moe_real
    print("  granite status:", moe_real.get("status"), "experts", moe_real["config_granite"]["num_local_experts"], "k", moe_real["config_granite"]["num_experts_per_tok"])
    if moe_real.get("status") != "ok":
        print("  motivo:", moe_real.get("erro") or moe_real.get("status"))

    print("=== A11.5 QAT vs PTQ (MLP) ===")
    t5 = time.perf_counter()
    qat = comparar_ptq_qat(passos=400, semente=0)
    qat["segundos"] = round(time.perf_counter() - t5, 3)
    payload["a11_5"] = qat
    print(f"  mse fp32={qat['mse_fp32']:.4f} ptq={qat['mse_ptq_depois']:.4f} qat={qat['mse_qat']:.4f}")

    skip_smol = bool(os.environ.get("TRILHA_A11_SEM_SMOL"))
    n_novos = int(os.environ.get("TRILHA_A11_N_NOVOS", "8"))
    if skip_smol:
        payload["a11_4"] = {"status": "pulado_env"}
        payload["a11_6"] = {"status": "pulado_env"}
        print("=== A11.4/A11.6 pulados (TRILHA_A11_SEM_SMOL) ===")
    else:
        print("=== A11.6 KV cache + batch (inclui prova MiniDecoder) ===")
        t6 = time.perf_counter()
        prova = prova_cache_minidecoder()
        med = medir_cache_e_batch(n_novos=n_novos)
        med["prova_minidecoder"] = prova
        med["segundos"] = round(time.perf_counter() - t6, 3)
        payload["a11_6"] = med
        print(
            f"  cache on={med['generate_use_cache_true_s']:.3f}s off={med['generate_use_cache_false_s']:.3f}s  "
            f"prova_attn_ok={prova['cache_attn_ok']}"
        )

        print("=== A11.4 PTQ SmolLM2 ===")
        t4 = time.perf_counter()
        ptq = comparar_ptq(n_novos=n_novos)
        ptq["segundos"] = round(time.perf_counter() - t4, 3)
        payload["a11_4"] = ptq
        print(
            f"  ppl fp32={ptq['fp32']['ppl']:.3f} int8={ptq['int8_dinamico']['ppl']:.3f} "
            f"int4={ptq['int4_grupo64_fake']['ppl']:.3f}"
        )

    payload["a11_3_lora_moe"] = {
        "status": "nao_executado",
        "motivo": "A6 não publicado; T4 não disponível nesta VM; LoRA do M09 permanece a ponte",
    }
    payload["segundos_total"] = round(time.perf_counter() - t0, 3)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")

    a1 = payload["a11_1"]["comparacao"]
    if not (a1["colapso_sem_aux"] and a1["mais_equilibrado_com_aux"]):
        raise SystemExit("CA11.1: colapso/aux não se comportou como esperado — veja o JSON.")
    if payload.get("a11_6") and payload["a11_6"].get("status") != "pulado_env":
        if not payload["a11_6"]["prova_minidecoder"]["cache_attn_ok"]:
            raise SystemExit("CA11.6: prova de cache da atenção falhou.")


if __name__ == "__main__":
    main()
