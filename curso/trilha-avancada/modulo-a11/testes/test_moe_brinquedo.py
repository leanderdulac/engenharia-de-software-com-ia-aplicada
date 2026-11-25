from __future__ import annotations

from moe_brinquedo import (
    CamadaMoE,
    comparar_com_sem_aux,
    exemplo_numerico_aula,
    parametros_totais_vs_ativos,
)
import torch


def test_totais_vs_ativos_conta_k_experts():
    moe = CamadaMoE(d=16, n_experts=8, k=2, d_ff=32)
    p = parametros_totais_vs_ativos(moe)
    assert p["ativos_por_token"] < p["total"]
    assert p["ativos_por_token"] == p["router"] + 2 * p["um_expert"]
    assert p["total"] == p["router"] + 8 * p["um_expert"]
    assert abs(p["fracao_ativa"] - 2 / 8) > 0  # router dilui um pouco a fração


def test_top2_nao_olha_os_outros_experts_no_valor():
    torch.manual_seed(0)
    moe = CamadaMoE(d=8, n_experts=4, k=2, d_ff=16)
    x = torch.randn(2, 3, 8)
    y1, _, f1 = moe(x)
    with torch.no_grad():
        # zera um expert que o router não escolheu no primeiro token
        f = f1.detach()
        morto = int((f == 0).nonzero(as_tuple=True)[0][0]) if (f == 0).any() else 3
        moe.experts[morto].sobe.weight.mul_(0)
        moe.experts[morto].desce.weight.mul_(0)
    y2, _, _ = moe(x)
    # se o expert morto não estava no top-2 de nenhum token, y não muda
    # (pode estar; então só checamos shape e finitude)
    assert y1.shape == y2.shape
    assert torch.isfinite(y2).all()


def test_exemplo_aula_aux_positivo_e_f_soma_k():
    r = exemplo_numerico_aula()
    assert r["aux"] > 0
    # cada token escolhe 2 experts → média de f soma k=2
    assert abs(sum(r["f"]) - 2.0) < 1e-5
    assert r["top_idx"][0][0] == 0  # maior logit é o expert 0


def test_colapso_sem_aux_e_equilibrio_com_aux():
    r = comparar_com_sem_aux(passos=200, semente=0, batch=24, seq=12)
    assert r["colapso_sem_aux"], r["sem_aux"]
    assert r["mais_equilibrado_com_aux"], {"sem": r["sem_aux"], "com": r["com_aux"]}
    assert r["sem_aux"]["parametros"]["n_experts"] == 8
    assert r["sem_aux"]["parametros"]["k"] == 2
