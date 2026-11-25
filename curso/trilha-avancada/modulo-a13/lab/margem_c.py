"""Margem geométrica e nº de vetores de suporte em função de C (soft margin)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.svm import SVC


def _margem_linear(clf: SVC) -> float | None:
    # w·x + b = 0; margem geométrica = 2 / ||w||
    w = clf.coef_[0]
    n = float(np.linalg.norm(w))
    if n == 0:
        return None
    return 2.0 / n


def curva_c(
    cs: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0),
    *,
    semente: int = 0,
) -> dict[str, Any]:
    X, y = make_blobs(
        n_samples=80,
        centers=2,
        cluster_std=2.4,
        random_state=semente,
        n_features=2,
    )
    linhas = []
    for c in cs:
        clf = SVC(kernel="linear", C=c)
        clf.fit(X, y)
        linhas.append(
            {
                "C": c,
                "n_sv": int(clf.n_support_.sum()),
                "margem": _margem_linear(clf),
                "acc_treino": float(clf.score(X, y)),
            }
        )
    return {
        "n": int(len(y)),
        "kernel": "linear",
        "linhas": linhas,
        "nota": (
            "C pequeno: mais violações, margem maior, em geral mais SVs. "
            "C grande: aproxima hard-margin."
        ),
    }
