"""Perdas da família de preferências, em log-probs já calculados.

Convenção: ``logp`` = soma (não média) dos log P dos tokens da *compleção*.
``logp_medio`` = soma / n_tokens. Tensores shape ``(B,)``.
"""

from __future__ import annotations

import math
from typing import Any

import torch
import torch.nn.functional as F


def perda_dpo(
    logp_w: torch.Tensor,
    logp_l: torch.Tensor,
    logp_w_ref: torch.Tensor,
    logp_l_ref: torch.Tensor,
    *,
    beta: float = 0.1,
) -> torch.Tensor:
    """Rafailov et al. 2023: ``-log σ(β (Δπ − Δref))``."""
    delta = (logp_w - logp_l) - (logp_w_ref - logp_l_ref)
    return -F.logsigmoid(beta * delta).mean()


def perda_ipo(
    logp_w: torch.Tensor,
    logp_l: torch.Tensor,
    logp_w_ref: torch.Tensor,
    logp_l_ref: torch.Tensor,
    *,
    beta: float = 0.1,
) -> torch.Tensor:
    """Azar et al. 2023: ``(h − 1/(2β))²`` com ``h = Δπ − Δref``."""
    h = (logp_w - logp_l) - (logp_w_ref - logp_l_ref)
    return ((h - 1.0 / (2.0 * beta)) ** 2).mean()


def perda_simpo(
    logp_w_medio: torch.Tensor,
    logp_l_medio: torch.Tensor,
    *,
    beta: float = 2.0,
    gamma: float = 0.5,
) -> torch.Tensor:
    """Meng et al. 2024: sem referência; margem γ. Usa média por token."""
    return -F.logsigmoid(beta * (logp_w_medio - logp_l_medio) - gamma).mean()


def perda_orpo(
    logp_w: torch.Tensor,
    logp_l: torch.Tensor,
    n_w: torch.Tensor,
    *,
    lambd: float = 0.1,
) -> torch.Tensor:
    """Hong et al. 2024 (esquema): SFT no chosen + λ · odds-ratio.

    ``L_SFT ≈ −logp_w / n_w``; odds-ratio em log-espaço com sigmoid da diferença.
    """
    sft = -(logp_w / n_w.clamp(min=1)).mean()
    or_term = -F.logsigmoid(logp_w - logp_l).mean()
    return sft + lambd * or_term


def perda_kto(
    logp: torch.Tensor,
    logp_ref: torch.Tensor,
    label_chosen: torch.Tensor,
    *,
    beta: float = 0.1,
    desejavel: float = 1.0,
    indesejavel: float = 1.0,
) -> torch.Tensor:
    """Ethayarajh et al. 2024 (esquema): valor Kahneman-Tversky em Δ = logp − logp_ref."""
    delta = logp - logp_ref
    z = beta * delta
    # chosen: 1 − σ(z); rejected: σ(z)  (queremos z alto em chosen)
    perda_pos = desejavel * (1.0 - torch.sigmoid(z))
    perda_neg = indesejavel * torch.sigmoid(z)
    m = label_chosen.float()
    return (m * perda_pos + (1.0 - m) * perda_neg).mean()


def tabela_no_lote(
    logp_w: torch.Tensor,
    logp_l: torch.Tensor,
    logp_w_ref: torch.Tensor,
    logp_l_ref: torch.Tensor,
    n_w: torch.Tensor,
    n_l: torch.Tensor,
    *,
    beta_dpo: float = 0.1,
) -> dict[str, Any]:
    logp_w_m = logp_w / n_w.clamp(min=1)
    logp_l_m = logp_l / n_l.clamp(min=1)
    kto_logp = torch.cat([logp_w, logp_l])
    kto_ref = torch.cat([logp_w_ref, logp_l_ref])
    kto_lab = torch.cat([torch.ones_like(logp_w), torch.zeros_like(logp_l)])
    return {
        "dpo_sigmoid": float(perda_dpo(logp_w, logp_l, logp_w_ref, logp_l_ref, beta=beta_dpo)),
        "ipo": float(perda_ipo(logp_w, logp_l, logp_w_ref, logp_l_ref, beta=beta_dpo)),
        "simpo": float(perda_simpo(logp_w_m, logp_l_m)),
        "orpo": float(perda_orpo(logp_w, logp_l, n_w)),
        "kto": float(perda_kto(kto_logp, kto_ref, kto_lab, beta=beta_dpo)),
        "beta_dpo": beta_dpo,
        "nao_e_ranking": True,
        "nota_unidades": (
            "DPO/SimPO/KTO em escala de -log σ; IPO e (h-1/(2β))²; ORPO mistura SFT. "
            "Comparar o numero cru entre linhas NAO e ranking de qualidade."
        ),
        "apis": {
            "dpo_sigmoid": "trl.DPOTrainer loss_type=sigmoid (estavel)",
            "ipo": "trl.DPOTrainer loss_type=ipo (estavel)",
            "kto": "trl.KTOTrainer (estavel)",
            "orpo": "trl.experimental.orpo.ORPOTrainer",
            "simpo": "trl.experimental.cpo.CPOTrainer loss_type=simpo",
        },
    }


def exemplo_numerico_aula() -> dict[str, float]:
    """Dois pares, números da aula, conferidos aqui."""
    logp_w = torch.tensor([-2.0, -1.5])
    logp_l = torch.tensor([-4.0, -1.6])
    logp_w_ref = torch.tensor([-2.2, -1.5])
    logp_l_ref = torch.tensor([-2.3, -1.55])
    n_w = torch.tensor([8.0, 4.0])
    n_l = torch.tensor([20.0, 5.0])
    tab = tabela_no_lote(logp_w, logp_l, logp_w_ref, logp_l_ref, n_w, n_l, beta_dpo=0.1)
    delta = (logp_w - logp_l) - (logp_w_ref - logp_l_ref)
    tab["delta"] = delta.tolist()
    tab["dpo_par0"] = float(-math.log(1 / (1 + math.exp(-0.1 * float(delta[0])))))
    return tab
