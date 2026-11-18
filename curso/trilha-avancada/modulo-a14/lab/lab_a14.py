#!/usr/bin/env python3
"""Labs A14 → ``modulo-a14/saidas/ca14.json``."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a0" / "lab"))

from curvas import knn, polinomio, ridge_vs_ols  # noqa: E402
from ic_binomial import ponte_historico  # noqa: E402
from interpolar import curva_features  # noqa: E402
from vazamento import duplicatas_no_teste, escala_antes_vs_depois, kfold_variabilidade  # noqa: E402
from versoes import rss_mb, versao  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca14.json"


def _ambiente() -> dict:
    try:
        from versoes import coletar_bancada

        return coletar_bancada()
    except ImportError:
        import platform
        import time

        return {
            "python": platform.python_version(),
            "device": "cpu",
            "gpu": None,
            "epoch_unix": int(time.time()),
            "pacotes": {"sklearn": versao("sklearn"), "torch": versao("torch")},
            "nota": "torch ausente nesta bancada; A14 é sklearn/numpy",
        }


def main() -> None:
    t0 = time.perf_counter()
    print("=== A14.1 IC Wilson/bootstrap nos números publicados A5/A7/A13 ===")
    ponte = ponte_historico()
    for chave in ("a5_eval_n2", "a5_se_n6", "a13_zhang_svm_n6", "a7_direto_n8"):
        b = ponte[chave]
        w = b["wilson95"]
        print(
            f"  {b['nome']}: {b['k']}/{b['n']}={b['acc']:.3f}  "
            f"Wilson[{w['lo']:.3f},{w['hi']:.3f}] largura={w['largura']:.3f} "
            f"vacuo_pratico={b['vacuo_pratico']}"
        )
    print("=== A14.2 vazamento: escala antes do split ===")
    esc = escala_antes_vs_depois()
    print(
        f"  antes={esc['acc_escala_antes_do_split']:.3f} "
        f"depois={esc['acc_escala_so_treino']:.3f} "
        f"delta={esc['delta_otimista']:.3f} otimista={esc['otimista']}"
    )
    print("=== A14.3 vazamento: duplicatas de treino no teste ===")
    dup = duplicatas_no_teste()
    print(
        f"  limpo={dup['acc_holdout_limpo']:.3f} "
        f"sujo={dup['acc_holdout_com_duplicata']:.3f} "
        f"delta={dup['delta_otimista']:.3f}"
    )
    print("=== A14.4 k-fold ===")
    kf = kfold_variabilidade()
    print(f"  accs={['%.3f' % a for a in kf['accs']]} media={kf['media']:.3f} sd={kf['desvio']:.3f}")
    print("=== A14.5 polinômio / k-NN / ridge ===")
    poly = polinomio()
    kn = knn()
    rg = ridge_vs_ols()
    print("  poly grau→mse_eval", [(ln["grau"], round(ln["mse_eval"], 3)) for ln in poly["linhas"]])
    print("  knn k→acc_eval", [(ln["k"], round(ln["acc_eval"], 3)) for ln in kn["linhas"]])
    print("=== A14.6 features aleatórias (pico de interpolação) ===")
    feat = curva_features()
    print(
        f"  pico_p={feat['pico_p']} mse={feat['pico_mse_eval']:.3f} "
        f"desceu={feat['desceu_depois_do_pico']}"
    )
    payload = {
        "ambiente": _ambiente(),
        "rss_processo_mb": rss_mb(),
        "sklearn": versao("sklearn"),
        "honestidade": {
            "smlbook_pdf": "nao_baixado; so citacao em leituras.md / NOTICE",
            "figuras_belkin_nakkiran": "nao_reproduzidas",
            "jsonl_m09": "nao_lido",
            "a5_n_eval_publicado": 2,
            "a13_n_eval_zhang": 6,
            "t4": "nao_calibrado",
        },
        "a14_1": ponte,
        "a14_2": esc,
        "a14_3": dup,
        "a14_4": kf,
        "a14_5": {"polinomio": poly, "knn": kn, "ridge": rg},
        "a14_6": feat,
        "segundos_total": round(time.perf_counter() - t0, 3),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
