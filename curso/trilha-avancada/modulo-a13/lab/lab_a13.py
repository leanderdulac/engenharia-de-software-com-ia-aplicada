#!/usr/bin/env python3
"""Labs A13 → ``modulo-a13/saidas/ca13.json``."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from classificar_frases import tabela as tabela_frases  # noqa: E402
from estilhaco import tabela as tabela_estilhaco  # noqa: E402
from limite_vc import ponte_a5  # noqa: E402
from margem_c import curva_c  # noqa: E402
from rotulos_aleatorios import experimento as exp_aleatorio  # noqa: E402
from versoes import coletar_bancada, rss_mb, versao  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca13.json"


def main() -> None:
    t0 = time.perf_counter()
    embed = os.environ.get("TRILHA_A13_EMBED", "1") != "0"
    print("=== A13.1 shattering 2D (3 pontos vs XOR) ===")
    est = tabela_estilhaco()
    print(
        f"  3pts estilhaça={est['tres_pontos']['estilhaça']} "
        f"{est['tres_pontos']['n_separaveis']}/{est['tres_pontos']['n_dicotomias']}  "
        f"4pts estilhaça={est['quatro_pontos']['estilhaça']} "
        f"XOR sep={est['xor']['linearmente_separavel']}"
    )
    print("=== A13.2 margem e n_sv vs C ===")
    curva = curva_c()
    for lin in curva["linhas"]:
        print(
            f"  C={lin['C']:<7} n_sv={lin['n_sv']:<3} "
            f"margem={lin['margem']:.4f} acc={lin['acc_treino']:.3f}"
        )
    print("=== A13.3 SVM linear/RBF vs logreg (frases) ===")
    frases = tabela_frases(tentar_embed=embed)
    print(f"  encoder_principal={frases['encoder_principal']}")
    for nome, bloco in frases["tfidf"].items():
        if nome in {"svm_linear", "svm_rbf", "logreg"}:
            print(
                f"  tfidf {nome}: treino={bloco['acc_treino']:.3f} "
                f"eval={bloco['acc_eval']:.3f}"
            )
    if frases["embeddings"].get("usou"):
        cmp_ = frases["embeddings"]["comparacao"]
        for nome in ("svm_linear", "svm_rbf", "logreg"):
            b = cmp_[nome]
            print(
                f"  embed {nome}: treino={b['acc_treino']:.3f} "
                f"eval={b['acc_eval']:.3f}"
            )
    print("=== A13.4 rótulos aleatórios (Zhang) ===")
    alea = exp_aleatorio()
    ra = alea["rotulos_aleatorios"]
    print(
        f"  svm_rbf treino={ra['svm_rbf']['acc_treino']:.3f} "
        f"eval={ra['svm_rbf']['acc_eval']:.3f}  "
        f"mlp treino={ra['mlp']['acc_treino']:.3f} "
        f"eval={ra['mlp']['acc_eval']:.3f}"
    )
    print("=== A13.5 ponte A5 → pergunta 1971 ===")
    ponte = ponte_a5()
    print(
        f"  A5 acc {ponte['acc_treino_a5']:.2f}/{ponte['acc_eval_a5']:.2f} "
        f"vacuo_lora={ponte['termo_lora']['vacuo']} "
        f"vacuo_vc3={ponte['termo_retas_vc3']['vacuo']}"
    )
    payload = {
        "ambiente": coletar_bancada(),
        "rss_processo_mb": rss_mb(),
        "sklearn": versao("sklearn"),
        "honestidade": {
            "jsonl_m09": "nao_lido; frases originais em frases_dominio.py",
            "sentence_transformers": "nao_usado; mean-pool SmolLM2 ou TF-IDF",
            "vc_dim_lora": "nao_calculada; h_proxy = n_params LoRA do A5 (aviso no JSON)",
            "zhang_cifar": "nao_reproduzido; espelho sklearn nas frases do domínio",
            "t4": "nao_calibrado",
        },
        "a13_1": est,
        "a13_2": curva,
        "a13_3": frases,
        "a13_4": alea,
        "a13_5": ponte,
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
