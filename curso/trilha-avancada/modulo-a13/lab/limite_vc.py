"""Termo aditivo estilo 1971/1999: quando o limite fica vazio (maior que 1).

Não é a VC-dimensão do LoRA nem do SmolLM2. É um *plug-in* da fórmula
clássica com um proxy de capacidade, para ver o bound estourar.

Forma usada (Vapnik 1999, IEEE TNN, ordem de grandeza do termo √):

    ε(h,n,δ) = sqrt( (h (ln(2n/h) + 1) + ln(4/δ)) / n )

Se h ≥ n, o termo não está definido de forma útil (já não há
convergência uniforme informativa com mais hipóteses que amostras):
devolvemos +inf. Se ε ≥ 1, o limite R ≤ R_emp + ε não informa nada
(risco já é ≤ 1).
"""

from __future__ import annotations

import math
from typing import Any


def termo_aditivo(h: float, n: int, delta: float = 0.1) -> float:
    if n <= 0 or h <= 0 or not (0.0 < delta < 1.0):
        raise ValueError("h, n > 0 e delta em (0,1)")
    if h >= n:
        return float("inf")
    inner = (h * (math.log(2.0 * n / h) + 1.0) + math.log(4.0 / delta)) / n
    return math.sqrt(inner)


def vacuo(h: float, n: int, delta: float = 0.1) -> dict[str, Any]:
    eps = termo_aditivo(h, n, delta)
    return {
        "h": h,
        "n": n,
        "delta": delta,
        "termo": eps if math.isfinite(eps) else "inf",
        "vacuo": bool(not math.isfinite(eps) or eps >= 1.0),
    }


def ponte_a5(
    acc_treino: float = 1.0,
    acc_eval: float = 0.5,
    n_treino: int = 4,
    n_params_lora: int = 460_800,
) -> dict[str, Any]:
    """Liga o SFT do A5 (treino 1,00 / eval 0,50) à pergunta de 1971."""
    v = vacuo(n_params_lora, n_treino)
    v_reta = vacuo(3, n_treino)
    return {
        "acc_treino_a5": acc_treino,
        "acc_eval_a5": acc_eval,
        "n_treino": n_treino,
        "h_proxy_lora": n_params_lora,
        "termo_lora": v,
        "termo_retas_vc3": v_reta,
        "aviso_proxy": (
            "h_proxy = nº de params LoRA NÃO é a VC-dimensão da rede. "
            "Só mostra que o bound clássico, plugado assim, já é vácuo."
        ),
        "pergunta_1971": (
            "a frequência empírica converge uniformemente à probabilidade "
            "na classe de eventos/hipóteses?"
        ),
        "leitura": (
            "R_emp=0 no treino e R_holdout=0,5: interpolou 4 diálogos. "
            "Com h_proxy = params LoRA o termo VC é vácuo; com h=3 (retas) "
            "o termo ainda é ≥1 porque n=4. VC não é a teoria de "
            "generalização dos LLMs."
        ),
    }
