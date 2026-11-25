"""Hold-out contaminado: seleção de features no conjunto inteiro; duplicatas de treino no teste."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.datasets import make_classification
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _lr() -> LogisticRegression:
    return LogisticRegression(max_iter=2000, solver="lbfgs")


def escala_antes_vs_depois(semente: int = 0) -> dict[str, Any]:
    """Selecionar K features com rótulos de *todo* o conjunto (inclui o teste)."""
    X, y = make_classification(
        n_samples=180,
        n_features=48,
        n_informative=6,
        n_redundant=2,
        flip_y=0.12,
        class_sep=0.7,
        random_state=semente,
    )
    k_best = 4
    # vazou: SelectKBest vê y do teste
    X_v = SelectKBest(f_classif, k=k_best).fit_transform(X, y)
    Xtr_l, Xte_l, ytr, yte = train_test_split(
        X_v, y, test_size=0.3, random_state=semente, stratify=y
    )
    acc_vazou = float(_lr().fit(Xtr_l, ytr).score(Xte_l, yte))

    Xtr, Xte, ytr2, yte2 = train_test_split(
        X, y, test_size=0.3, random_state=semente, stratify=y
    )
    pipe = Pipeline(
        [
            ("sel", SelectKBest(f_classif, k=k_best)),
            ("esc", StandardScaler()),
            ("lr", _lr()),
        ]
    )
    acc_ok = float(pipe.fit(Xtr, ytr2).score(Xte, yte2))
    return {
        "n_treino": int(len(ytr2)),
        "n_eval": int(len(yte2)),
        "n_features": int(X.shape[1]),
        "k_best": k_best,
        "mecanismo": "SelectKBest no X,y inteiro vs só treino",
        "acc_escala_antes_do_split": acc_vazou,
        "acc_escala_so_treino": acc_ok,
        "delta_otimista": acc_vazou - acc_ok,
        "otimista": bool(acc_vazou > acc_ok + 1e-12),
    }


def duplicatas_no_teste(semente: int = 0, frac: float = 0.5) -> dict[str, Any]:
    """k-NN 1-vizinho interpola o treino: injetar cópias só pode subir a acc do eval."""
    X, y = make_classification(
        n_samples=100,
        n_features=10,
        n_informative=4,
        flip_y=0.15,
        class_sep=0.65,
        random_state=semente,
    )
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.35, random_state=semente, stratify=y
    )
    clf = KNeighborsClassifier(n_neighbors=1)
    clf.fit(Xtr, ytr)
    acc_limpo = float(clf.score(Xte, yte))
    acc_tr = float(clf.score(Xtr, ytr))
    rng = np.random.default_rng(semente)
    n_copy = max(1, int(frac * len(ytr)))
    idx = rng.choice(len(ytr), size=n_copy, replace=False)
    Xte_sujo = np.vstack([Xte, Xtr[idx]])
    yte_sujo = np.concatenate([yte, ytr[idx]])
    acc_sujo = float(clf.score(Xte_sujo, yte_sujo))
    return {
        "n_treino": int(len(ytr)),
        "n_eval_limpo": int(len(yte)),
        "n_injetados": n_copy,
        "classificador": "KNeighborsClassifier(k=1)",
        "acc_treino": acc_tr,
        "acc_holdout_limpo": acc_limpo,
        "acc_holdout_com_duplicata": acc_sujo,
        "delta_otimista": acc_sujo - acc_limpo,
        "otimista": bool(acc_sujo > acc_limpo + 1e-12),
        "nota": "espelho raso de contaminação de benchmark: o teste viu o treino",
    }


def kfold_variabilidade(semente: int = 0, k: int = 5) -> dict[str, Any]:
    X, y = make_classification(
        n_samples=80,
        n_features=10,
        n_informative=4,
        flip_y=0.1,
        random_state=semente,
    )
    cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=semente)
    pipe = Pipeline([("esc", StandardScaler()), ("lr", _lr())])
    accs = cross_val_score(pipe, X, y, cv=cv)
    return {
        "k": k,
        "n": int(len(y)),
        "accs": [float(a) for a in accs],
        "media": float(accs.mean()),
        "desvio": float(accs.std(ddof=1) if len(accs) > 1 else 0.0),
        "min": float(accs.min()),
        "max": float(accs.max()),
    }
