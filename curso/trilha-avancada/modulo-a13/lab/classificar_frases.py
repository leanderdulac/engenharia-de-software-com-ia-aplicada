"""SVM linear, SVM RBF e regressão logística sobre frases do domínio.

Encoder: tenta mean-pool do SmolLM2-135M (já na bancada da trilha).
Se falhar (download, RAM, pad), cai em TF-IDF e declara no JSON.
Não usa sentence-transformers (não está em requirements).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from frases_dominio import EVAL, TREINO, xy


MODELO_HF = "HuggingFaceTB/SmolLM2-135M"


def _tfidf(
    tr: list[str], ev: list[str]
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    Xtr = vec.fit_transform(tr)
    Xev = vec.transform(ev)
    meta = {
        "encoder": "tfidf",
        "n_features": int(Xtr.shape[1]),
        "nota": "TF-IDF unigrama+bigrama; fallback ou via explícita",
    }
    return Xtr, Xev, meta


def _mean_pool_smollm2(
    tr: list[str], ev: list[str]
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]] | None:
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError:
        return None

    try:
        tok = AutoTokenizer.from_pretrained(MODELO_HF)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        model = AutoModel.from_pretrained(MODELO_HF)
        model.eval()

        def embed(textos: list[str]) -> np.ndarray:
            batch = tok(
                textos,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=64,
            )
            with torch.no_grad():
                out = model(**batch)
            h = out.last_hidden_state
            mask = batch["attention_mask"].unsqueeze(-1).to(h.dtype)
            pooled = (h * mask).sum(1) / mask.sum(1).clamp(min=1e-6)
            return pooled.float().cpu().numpy()

        Xtr = embed(tr)
        Xev = embed(ev)
        return Xtr, Xev, {
            "encoder": "smollm2-135m-meanpool",
            "n_features": int(Xtr.shape[1]),
            "modelo": MODELO_HF,
            "nota": "média de last_hidden_state mascarada; Apache-2.0",
        }
    except Exception:
        return None


def _score(clf: Any, Xtr: Any, ytr: list[int], Xev: Any, yev: list[int]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "acc_treino": float(clf.score(Xtr, ytr)),
        "acc_eval": float(clf.score(Xev, yev)),
    }
    if hasattr(clf, "n_support_"):
        out["n_sv"] = int(np.sum(clf.n_support_))
    return out


def comparar(Xtr: Any, ytr: list[int], Xev: Any, yev: list[int]) -> dict[str, Any]:
    linear = SVC(kernel="linear", C=1.0)
    rbf = SVC(kernel="rbf", C=1.0, gamma="scale")
    log = LogisticRegression(max_iter=2000, solver="lbfgs")
    linear.fit(Xtr, ytr)
    rbf.fit(Xtr, ytr)
    log.fit(Xtr, ytr)
    return {
        "svm_linear": _score(linear, Xtr, ytr, Xev, yev),
        "svm_rbf": _score(rbf, Xtr, ytr, Xev, yev),
        "logreg": _score(log, Xtr, ytr, Xev, yev),
        "uso_hoje": (
            "baseline sobre embeddings; classificador leve; "
            "guardrail raso (domínio vs fora) antes do LLM"
        ),
    }


def tabela(tentar_embed: bool = True) -> dict[str, Any]:
    tr_txt, ytr = xy(TREINO)
    ev_txt, yev = xy(EVAL)
    Xtr_t, Xev_t, meta_t = _tfidf(tr_txt, ev_txt)
    bloco_t = comparar(Xtr_t, ytr, Xev_t, yev)
    bloco_t["encoder"] = meta_t

    embed: dict[str, Any] = {"tentado": bool(tentar_embed), "usou": False}
    if tentar_embed:
        got = _mean_pool_smollm2(tr_txt, ev_txt)
        if got is not None:
            Xtr_e, Xev_e, meta_e = got
            bloco_e = comparar(Xtr_e, ytr, Xev_e, yev)
            bloco_e["encoder"] = meta_e
            embed = {"tentado": True, "usou": True, "comparacao": bloco_e}
        else:
            embed = {
                "tentado": True,
                "usou": False,
                "motivo": "mean-pool SmolLM2 indisponível; TF-IDF declarado",
            }

    return {
        "n_treino": len(ytr),
        "n_eval": len(yev),
        "split_disjunto": True,
        "tfidf": bloco_t,
        "embeddings": embed,
        "encoder_principal": (
            "smollm2-135m-meanpool" if embed.get("usou") else "tfidf"
        ),
    }
