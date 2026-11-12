#!/usr/bin/env python3
"""Labs A1 → ``modulo-a1/saidas/ca1.json``.

    python modulo-a1/lab/lab_a1.py

    TRILHA_A1_MODELO   id HF (padrão: HuggingFaceTB/SmolLM2-135M)
    TRILHA_A1_PROMPT   texto cujo último logit vira softmax/entropia
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
A2_LAB = AQUI.parents[1] / "modulo-a2" / "lab"
sys.path.insert(0, str(A2_LAB))

from ambiente import coletar_ambiente  # noqa: E402
from amostragem import (  # noqa: E402
    conferir_warpers_hf,
    curva_entropia,
    generate_greedy_hf,
    greedy_autorregressivo,
    softmax,
)
from tokenizacao import tabela_pt_en  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca1.json"
MODELO = os.environ.get("TRILHA_A1_MODELO", "HuggingFaceTB/SmolLM2-135M")
PROMPT = os.environ.get(
    "TRILHA_A1_PROMPT",
    "Responda apenas o numero inteiro.\n2+2=",
)


def _serializavel(x):
    if isinstance(x, dict):
        return {k: _serializavel(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_serializavel(v) for v in x]
    if isinstance(x, float):
        return x
    if isinstance(x, torch.Tensor):
        return x.tolist()
    return x


def lab_a1_1() -> dict:
    t0 = time.perf_counter()
    tab = tabela_pt_en()
    tab["segundos"] = round(time.perf_counter() - t0, 3)
    return tab


def lab_a1_2() -> dict:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.perf_counter()
    device = "cpu"
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    model.to(device)
    model.eval()

    nossa = greedy_autorregressivo(model, tok, PROMPT, max_novos=8, device=device)
    hf = generate_greedy_hf(model, tok, PROMPT, max_novos=8, device=device)
    ids_ok = nossa["ids_novos"] == hf["ids_novos"]

    enc = tok(PROMPT, return_tensors="pt")
    with torch.no_grad():
        logits = model(enc.input_ids.to(device)).logits[0, -1, :].cpu()
    warpers = conferir_warpers_hf(logits)
    temps = [0.1, 0.5, 1.0, 1.5, 2.0]
    curva = curva_entropia(logits, temps)
    p = softmax(logits)
    top5 = torch.topk(p, 5)
    top5_ids = top5.indices.tolist()
    top5_toks = tok.convert_ids_to_tokens(top5_ids)

    # T→0: greedy do softmax(z/T) deve coincidir com argmax(z)
    p_frio = softmax(logits / 0.05)
    greedy_frio = int(p_frio.argmax())
    greedy_z = int(logits.argmax())

    cfg = model.config
    janela = int(getattr(cfg, "max_position_embeddings", 0) or 0)
    d = int(cfg.hidden_size)
    v = int(cfg.vocab_size)

    return {
        "modelo": MODELO,
        "prompt": PROMPT,
        "greedy_nossa": nossa,
        "greedy_hf": hf,
        "greedy_ids_iguais": ids_ok,
        "warpers_hf": warpers,
        "passou_warpers": all(v < 1e-5 for v in warpers.values()),
        "passou_greedy": ids_ok,
        "greedy_temperatura_baixa_igual_argmax": greedy_frio == greedy_z,
        "top5": [{"id": i, "token": t, "p": float(p)} for i, t, p in zip(top5_ids, top5_toks, top5.values.tolist())],
        "entropia": curva,
        "config": {
            "vocab_size": v,
            "hidden_size": d,
            "max_position_embeddings": janela,
            "tie_word_embeddings": bool(getattr(cfg, "tie_word_embeddings", False)),
        },
        "segundos": round(time.perf_counter() - t0, 3),
    }


def main() -> None:
    t0 = time.perf_counter()
    print("=== Lab A1.1 — tokenização PT vs EN ===")
    a11 = lab_a1_1()
    sm = a11["pares"][0]["smollm2"]
    print(
        f"  sinistro SmolLM2  PT={sm['pt']['n_tokens']} tok  EN={sm['en']['n_tokens']} tok  "
        f"razão PT/EN={sm['razao_pt_en']:.3f}"
    )
    print(f"  quebra 'Segurado': {a11['quebra_bpe']['smollm2']}")
    print("=== Lab A1.2 — softmax / greedy / warpers / entropia ===")
    a12 = lab_a1_2()
    print(
        f"  greedy ids iguais ao generate: {a12['greedy_ids_iguais']}  "
        f"texto={a12['greedy_nossa']['texto']!r}"
    )
    w = a12["warpers_hf"]
    print(
        f"  Δ T={w['delta_temperatura']:.3e}  Δ top-k={w['delta_top_k']:.3e}  "
        f"Δ top-p={w['delta_top_p']:.3e}"
    )
    print(f"  entropia T=0,1 → T=2: {[round(c['entropia_nats'], 3) for c in a12['entropia']]}")
    payload = {
        "ambiente": coletar_ambiente(),
        "honestidade": {
            "a0": "esqueleto; ambiente coletado como no A2, sem bancada.json",
            "m01": "sliders exemplo-04 citados, não copiados; top-p não é aula no tronco",
        },
        "a1_1": a11,
        "a1_2": a12,
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(_serializavel(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
