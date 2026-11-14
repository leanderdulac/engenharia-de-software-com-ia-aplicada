"""Shattering em R²: VC das semirretas/hiperplanos lineares.

3 pontos não colineares: as 8 dicotomias são linearmente separáveis
(VC ≥ 3). 4 vértices de um quadrado: o XOR não tem reta (VC das retas em
R² é 3, não 4).
"""

from __future__ import annotations

import warnings
from itertools import product
from typing import Any

import numpy as np
from sklearn.svm import SVC

P3 = np.array([[0.0, 0.0], [1.0, 0.0], [0.25, 0.9]])
# quadrado: XOR = vértices opostos na mesma classe
P4 = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
Y_XOR = np.array([0, 1, 1, 0])


def _separavel_linear(X: np.ndarray, y: np.ndarray) -> bool:
    classes = set(y.tolist())
    if len(classes) == 1:
        return True
    clf = SVC(kernel="linear", C=1e6, max_iter=20_000)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        clf.fit(X, y)
    return float(clf.score(X, y)) == 1.0


def dicotomias(X: np.ndarray) -> dict[str, Any]:
    n = len(X)
    ok = 0
    falhas: list[list[int]] = []
    for bits in product([0, 1], repeat=n):
        y = np.array(bits)
        if _separavel_linear(X, y):
            ok += 1
        else:
            falhas.append(list(bits))
    return {
        "n_pontos": n,
        "n_dicotomias": 2**n,
        "n_separaveis": ok,
        "estilhaça": ok == 2**n,
        "falhas": falhas,
    }


def xor_falha() -> dict[str, Any]:
    sep = _separavel_linear(P4, Y_XOR)
    return {
        "pontos": P4.tolist(),
        "rotulos_xor": Y_XOR.tolist(),
        "linearmente_separavel": sep,
        "nota": "dois pares de vértices opostos: nenhuma reta separa",
    }


def tabela() -> dict[str, Any]:
    d3 = dicotomias(P3)
    d4 = dicotomias(P4)
    x = xor_falha()
    return {
        "tres_pontos": d3,
        "quatro_pontos": d4,
        "xor": x,
        "vc_retas_r2": 3,
        "conclusao": (
            "3 pontos não colineares estilhaçam; 4 no quadrado não "
            "(XOR entre as falhas)."
        ),
    }
