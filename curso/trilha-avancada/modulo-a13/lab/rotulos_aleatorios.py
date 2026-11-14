"""Rótulos aleatórios no espírito Zhang et al. 2017 (arXiv 1611.03530).

Treina com y embaralhado. Se a classe for rica o bastante, acc_treino → 1
e acc_teste fica no acaso. Espelha o SFT do A5 (1,00 vs 0,50) em escala
sklearn: interpolar não implica generalizar.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from frases_dominio import EVAL, TREINO, xy


def _fit_score(clf: Any, Xtr: Any, ytr: np.ndarray, Xev: Any, yev: np.ndarray) -> dict[str, Any]:
    clf.fit(Xtr, ytr)
    return {
        "acc_treino": float(clf.score(Xtr, ytr)),
        "acc_eval": float(clf.score(Xev, yev)),
    }


def experimento(semente: int = 0) -> dict[str, Any]:
    tr_txt, ytr = xy(TREINO)
    ev_txt, yev = xy(EVAL)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    Xtr = vec.fit_transform(tr_txt)
    Xev = vec.transform(ev_txt)
    ytr_np = np.array(ytr)
    yev_np = np.array(yev)
    rng = np.random.RandomState(semente)
    y_rand = rng.permutation(ytr_np)

    svm = SVC(kernel="rbf", C=10.0, gamma="scale")
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        max_iter=2000,
        random_state=semente,
        solver="lbfgs",
    )
    # referência: rótulos verdadeiros
    svm_true = _fit_score(SVC(kernel="rbf", C=10.0, gamma="scale"), Xtr, ytr_np, Xev, yev_np)
    mlp_true = _fit_score(
        MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=2000, random_state=semente, solver="lbfgs"),
        Xtr,
        ytr_np,
        Xev,
        yev_np,
    )
    svm_rand = _fit_score(svm, Xtr, y_rand, Xev, yev_np)
    mlp_rand = _fit_score(mlp, Xtr, y_rand, Xev, yev_np)
    return {
        "n_treino": int(len(ytr)),
        "n_eval": int(len(yev)),
        "n_features": int(Xtr.shape[1]),
        "fracao_rotulos_trocados": float(np.mean(y_rand != ytr_np)),
        "rotulos_verdadeiros": {"svm_rbf": svm_true, "mlp": mlp_true},
        "rotulos_aleatorios": {"svm_rbf": svm_rand, "mlp": mlp_rand},
        "leitura_zhang": (
            "se acc_treino_aleatório ≈ 1 e acc_eval ≈ acaso, a hipótese "
            "decorou o ruído — o mesmo fenômeno que Zhang et al. 2017 "
            "mostraram em redes profundas (arXiv 1611.03530)."
        ),
    }
