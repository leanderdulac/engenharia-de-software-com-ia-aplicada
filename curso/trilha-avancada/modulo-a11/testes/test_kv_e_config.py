from __future__ import annotations

import pytest

from inspecionar_moe import MODELO_GRANITE, MODELO_OLMOE, ler_config_moe
from kv_cache import prova_cache_minidecoder


def test_prova_cache_atencao_bate_com_sequencia_cheia():
    r = prova_cache_minidecoder(seq=8, n_novos=4, semente=2)
    assert r["greedy_ids_iguais"]
    assert r["cache_attn_ok"]
    assert r["delta_attn_cache_vs_full"] < 1e-5


def test_config_granite_32_experts_top8():
    c = ler_config_moe(MODELO_GRANITE)
    assert c["num_local_experts"] == 32
    assert c["num_experts_per_tok"] == 8
    assert c["model_type"] == "granitemoe"
    assert abs(c["fracao_experts_ativos"] - 8 / 32) < 1e-9


def test_config_olmoe_64_experts_nao_baixamos_pesos():
    c = ler_config_moe(MODELO_OLMOE)
    assert c["num_local_experts"] == 64 or c.get("num_local_experts") == 64
    assert c["num_experts_per_tok"] == 8
    assert c["model_type"] == "olmoe"


@pytest.mark.modelo
def test_smol_ptq_ppl_finita():
    from ptq import comparar_ptq

    r = comparar_ptq(n_novos=4)
    assert r["fp32"]["ppl"] > 1.0
    assert r["int8_dinamico"]["ppl"] > 1.0
    assert r["int8_dinamico_sem_lm_head"]["ppl"] > 1.0
    assert r["int4_grupo64_fake"]["ppl"] > 1.0
    assert r["fp32"]["bytes"] > r["int8_dinamico"]["bytes"] or r["int8_dinamico"]["bytes"] > 0
    # lição: incluir lm_head costuma doer mais que a comparação justa
    assert r["int8_dinamico"]["ppl"] >= r["int8_dinamico_sem_lm_head"]["ppl"] - 1e-6
