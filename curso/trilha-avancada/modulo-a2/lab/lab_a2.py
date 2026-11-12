#!/usr/bin/env python3
"""Roda os labs A2.1 e A2.2 e grava ``modulo-a2/saidas/ca2.json``.

Uso (na pasta ``curso/trilha-avancada/``):

    python modulo-a2/lab/lab_a2.py

Variáveis:

    TRILHA_A2_MODELO   id Hugging Face (padrão: HuggingFaceTB/SmolLM2-135M)
    TRILHA_A2_FRASE    texto a inspecionar
    TRILHA_A2_CAMADA   índice do bloco reconstruído (padrão: 0)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from ambiente import coletar_ambiente  # noqa: E402
from atencao import atencao_igual_ao_pytorch, prova_que_o_futuro_nao_vaza  # noqa: E402
from exemplo_numerico import calcular as calcular_exemplo  # noqa: E402
from inspecionar_modelo import FRASE_PADRAO, inspecionar, mapa_ascii  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca2.json"


def lab_a2_1(semente: int = 0) -> dict:
    g = torch.Generator().manual_seed(semente)
    q = torch.randn(2, 4, 12, 8, generator=g)
    k = torch.randn(2, 4, 12, 8, generator=g)
    v = torch.randn(2, 4, 12, 8, generator=g)
    _, _, delta = atencao_igual_ao_pytorch(q, k, v, causal=True)
    causal_ok = prova_que_o_futuro_nao_vaza(semente=semente)
    exemplo = calcular_exemplo()
    return {
        "diff_max_vs_sdpa": delta,
        "limiar_ca2_1": 1e-5,
        "passou_diff": delta < 1e-5,
        "causal_ok": bool(causal_ok),
        "exemplo_aula_delta": float(exemplo["delta"]),
        "exemplo_aula_pesos_pos1": exemplo["pesos"][1].tolist(),
        "exemplo_aula_saida_pos1": exemplo["saida"][1].tolist(),
    }


def lab_a2_2() -> dict:
    frase = os.environ.get("TRILHA_A2_FRASE", FRASE_PADRAO)
    camada = int(os.environ.get("TRILHA_A2_CAMADA", "0"))
    t0 = time.perf_counter()
    r = inspecionar(frase=frase, camada=camada, cabeca=0)
    r["segundos"] = round(time.perf_counter() - t0, 3)
    r["ascii_cabeca0"] = mapa_ascii(r["tokens"], r["atencao"]["mapa"])
    r["passou_reconstrucao"] = r["bloco_reconstruido"]["diff_max"] < 1e-3
    r["passou_contagem"] = r["parametros"]["erro_relativo"] <= 0.001
    return r


def main() -> None:
    t0 = time.perf_counter()
    print("=== Lab A2.1 — atenção do zero ===")
    a21 = lab_a2_1()
    print(
        f"  Δ máx vs SDPA = {a21['diff_max_vs_sdpa']:.3e}  "
        f"(limiar {a21['limiar_ca2_1']})  causal_ok={a21['causal_ok']}"
    )
    print("=== Lab A2.2 — modelo real ===")
    a22 = lab_a2_2()
    print(f"  modelo: {a22['modelo']}")
    cfg = a22["config"]
    print(
        f"  camadas={cfg['num_hidden_layers']}  d={cfg['hidden_size']}  "
        f"Q={cfg['num_attention_heads']} KV={cfg['num_key_value_heads']}  "
        f"GQA={cfg['gqa']}  act={cfg['hidden_act']}  rope_θ={cfg['rope_theta']}"
    )
    p = a22["parametros"]
    print(
        f"  parâmetros: {p['total_unico']} (HF {p['num_parameters']})  "
        f"erro relativo={p['erro_relativo']:.3e}"
    )
    print("  por componente:", p["por_componente"])
    b = a22["bloco_reconstruido"]
    print(
        f"  bloco {b['camada']} reconstruído: Δmáx={b['diff_max']:.3e}  "
        f"Δmédia={b['diff_media']:.3e}  Δatenção={b['diff_atencao_max']:.3e}"
    )
    print("  tokens:", a22["tokens"])
    print("  mapa (camada {}, cabeça 0):\n{}".format(a22["atencao"]["camada"], a22["ascii_cabeca0"]))
    payload = {
        "ambiente": coletar_ambiente(),
        "a2_1": a21,
        "a2_2": {
            k: v
            for k, v in a22.items()
            if k != "ascii_cabeca0"
        },
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    # mapa completo é grande; no JSON fica, o ascii é só stdout
    payload["a2_2"]["ascii_cabeca0"] = a22["ascii_cabeca0"]
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")
    if not (a21["passou_diff"] and a21["causal_ok"] and a22["passou_reconstrucao"] and a22["passou_contagem"]):
        raise SystemExit("CA2: algum critério falhou — veja o JSON.")


if __name__ == "__main__":
    main()
