"""Pico perto da interpolação: OLS em p colunas, n fixo.

Experimento original desta trilha — não reproduz figuras de Belkin/Nakkiran.
Colunas 0..d_true-1 carregam o sinal; o resto é ruído. p atravessa n.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def curva_features(
    n_treino: int = 40,
    n_eval: int = 160,
    d_true: int = 6,
    p_max: int = 160,
    semente: int = 0,
    ruido: float = 0.4,
) -> dict[str, Any]:
    rng = np.random.default_rng(semente)
    n_tot = n_treino + n_eval
    # pool largo de colunas; as primeiras d_true geram y
    X_pool = rng.normal(size=(n_tot, p_max))
    w = rng.normal(size=d_true)
    y = X_pool[:, :d_true] @ w + ruido * rng.normal(size=n_tot)
    ytr, yte = y[:n_treino], y[n_treino:]
    ps = (6, 12, 24, 36, 40, 44, 80, 160)
    linhas = []
    for p in ps:
        Phi_tr = X_pool[:n_treino, :p]
        Phi_te = X_pool[n_treino:, :p]
        coef, *_ = np.linalg.lstsq(Phi_tr, ytr, rcond=None)
        mse_tr = float(np.mean((Phi_tr @ coef - ytr) ** 2))
        mse_te = float(np.mean((Phi_te @ coef - yte) ** 2))
        linhas.append(
            {
                "p": p,
                "p_sobre_n": p / n_treino,
                "interpola": bool(mse_tr < 1e-8),
                "mse_treino": mse_tr,
                "mse_eval": mse_te,
            }
        )
    evals = [ln["mse_eval"] for ln in linhas]
    i_pico = int(np.argmax(evals))
    depois = evals[i_pico + 1 :] if i_pico + 1 < len(evals) else []
    desceu = bool(depois) and min(depois) < evals[i_pico] - 1e-9
    return {
        "n_treino": n_treino,
        "n_eval": n_eval,
        "d_true": d_true,
        "linhas": linhas,
        "pico_p": linhas[i_pico]["p"],
        "pico_mse_eval": evals[i_pico],
        "desceu_depois_do_pico": desceu,
        "nota": (
            "pico clássico perto de p≈n. Segunda descida, se aparecer, é o "
            "fenômeno Belkin/Nakkiran neste desenho — não uma figura deles."
        ),
    }
