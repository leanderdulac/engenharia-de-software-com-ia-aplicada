"""Curvas de complexidade: polinômio 1D e k-NN. Regularização ridge."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.datasets import make_classification


def _seno(n: int, semente: int, ruido: float = 0.35) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(semente)
    x = rng.uniform(0.0, 1.0, size=(n, 1))
    y = np.sin(2.0 * np.pi * x[:, 0]) + ruido * rng.normal(size=n)
    return x, y


def polinomio(semente: int = 0, graus: tuple[int, ...] = (1, 2, 4, 8, 12, 16)) -> dict[str, Any]:
    x, y = _seno(80, semente)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.35, random_state=semente)
    linhas = []
    for g in graus:
        pipe = Pipeline(
            [
                ("poly", PolynomialFeatures(degree=g, include_bias=True)),
                ("lin", LinearRegression()),
            ]
        )
        pipe.fit(xtr, ytr)
        linhas.append(
            {
                "grau": g,
                "mse_treino": float(np.mean((pipe.predict(xtr) - ytr) ** 2)),
                "mse_eval": float(np.mean((pipe.predict(xte) - yte) ** 2)),
            }
        )
    return {"n_treino": int(len(ytr)), "n_eval": int(len(yte)), "linhas": linhas}


def ridge_vs_ols(semente: int = 0, grau: int = 14, alphas: tuple[float, ...] = (0.0, 0.01, 1.0, 100.0)) -> dict[str, Any]:
    x, y = _seno(80, semente)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.35, random_state=semente)
    linhas = []
    for a in alphas:
        modelo: Any
        if a == 0.0:
            modelo = LinearRegression()
            nome = "ols"
        else:
            modelo = Ridge(alpha=a)
            nome = "ridge"
        pipe = Pipeline(
            [
                ("poly", PolynomialFeatures(degree=grau, include_bias=True)),
                ("m", modelo),
            ]
        )
        pipe.fit(xtr, ytr)
        linhas.append(
            {
                "modelo": nome,
                "alpha": a,
                "mse_treino": float(np.mean((pipe.predict(xtr) - ytr) ** 2)),
                "mse_eval": float(np.mean((pipe.predict(xte) - yte) ** 2)),
            }
        )
    return {"grau": grau, "n_treino": int(len(ytr)), "linhas": linhas}


def knn(semente: int = 0, ks: tuple[int, ...] = (1, 3, 9, 21)) -> dict[str, Any]:
    X, y = make_classification(
        n_samples=140,
        n_features=8,
        n_informative=3,
        flip_y=0.08,
        class_sep=0.85,
        random_state=semente,
    )
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=semente, stratify=y)
    sc = StandardScaler().fit(Xtr)
    Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)
    linhas = []
    for k in ks:
        clf = KNeighborsClassifier(n_neighbors=k)
        clf.fit(Xtr_s, ytr)
        linhas.append(
            {
                "k": k,
                "acc_treino": float(clf.score(Xtr_s, ytr)),
                "acc_eval": float(clf.score(Xte_s, yte)),
            }
        )
    return {"n_treino": int(len(ytr)), "n_eval": int(len(yte)), "linhas": linhas}
