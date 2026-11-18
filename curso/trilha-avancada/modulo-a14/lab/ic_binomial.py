"""Intervalos para uma acurácia binomial: Wilson e bootstrap percentil.

Não é um bound VC. É incerteza amostral do hold-out quando n é pequeno
(A5 n=2, A13 n=6, A7 n=8).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

# Números publicados (autoria), não relidos de saidas/ gitignoradas.
A5_EVAL = {"origem": "modulo-a5/execucao/ca5-autoria.json", "k": 1, "n": 2, "acc": 0.5}
A7_DIRETO = {"origem": "modulo-a7/execucao/ca7-autoria.json", "k": 3, "n": 8, "acc": 0.375}
A13_ZHANG_SVM = {
    "origem": "modulo-a13/execucao/ca13-autoria.json a13_4.rotulos_aleatorios.svm_rbf",
    "k": 3,
    "n": 6,
    "acc": 0.5,
}
# pedagogia: se o eval do A5 tivesse o n do hold-out A13, com a mesma taxa
A5_SE_N6 = {"origem": "hipotese pedagogica (nao medido no A5)", "k": 3, "n": 6, "acc": 0.5}


def wilson(k: int, n: int, z: float = 1.96) -> dict[str, float]:
    if n <= 0 or k < 0 or k > n:
        raise ValueError("k em 0..n, n>0")
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    centro = (p + z2 / (2.0 * n)) / den
    rad = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / den
    return {
        "p": p,
        "lo": max(0.0, centro - rad),
        "hi": min(1.0, centro + rad),
        "largura": min(1.0, centro + rad) - max(0.0, centro - rad),
    }


def bootstrap_seq(k: int, n: int, n_boot: int = 4000, semente: int = 0, alpha: float = 0.05) -> dict[str, float]:
    if n <= 0 or k < 0 or k > n:
        raise ValueError("k em 0..n, n>0")
    rng = np.random.default_rng(semente)
    seq = np.array([1] * k + [0] * (n - k), dtype=np.float64)
    stats = np.empty(n_boot)
    for i in range(n_boot):
        stats[i] = seq[rng.integers(0, n, n)].mean()
    lo, hi = np.quantile(stats, [alpha / 2.0, 1.0 - alpha / 2.0])
    return {
        "p": float(k / n),
        "lo": float(lo),
        "hi": float(hi),
        "largura": float(hi - lo),
        "n_boot": n_boot,
    }


def bloco(nome: str, meta: dict[str, Any], semente: int = 0) -> dict[str, Any]:
    k, n = int(meta["k"]), int(meta["n"])
    w = wilson(k, n)
    b = bootstrap_seq(k, n, semente=semente)
    return {
        "nome": nome,
        "origem": meta["origem"],
        "k": k,
        "n": n,
        "acc": meta["acc"],
        "wilson95": w,
        "bootstrap95": b,
        "vacuo_pratico": bool(w["largura"] >= 0.5),
    }


def ponte_historico(semente: int = 0) -> dict[str, Any]:
    return {
        "a5_eval_n2": bloco("A5 eval", A5_EVAL, semente),
        "a5_se_n6": bloco("A5 se n=6 (não medido)", A5_SE_N6, semente),
        "a13_zhang_svm_n6": bloco("A13 Zhang SVM RBF eval", A13_ZHANG_SVM, semente),
        "a7_direto_n8": bloco("A7 acc_direto", A7_DIRETO, semente),
        "leitura": (
            "n=2 (A5 publicado) deixa o IC quase [0,1]. n=6 (hold-out A13) "
            "ainda é largo. O bound VC do A13 era vácuo; o IC empírico também "
            "não fecha a conta com n tão pequeno."
        ),
    }
