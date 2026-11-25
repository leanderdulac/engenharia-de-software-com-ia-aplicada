from __future__ import annotations

import pytest
import torch

from inspecionar_modelo import FRASE_PADRAO, contar_parametros, ler_config, reconstruir_bloco

pytestmark = pytest.mark.modelo


def test_config_tem_pecas_de_llm_moderno(modelo_pequeno):
    _, model, _, _ = modelo_pequeno
    cfg = ler_config(model)
    assert cfg["num_hidden_layers"] >= 1
    assert cfg["num_attention_heads"] >= cfg["num_key_value_heads"]
    assert cfg["hidden_act"] in {"silu", "gelu_pytorch_tanh", "gelu"}
    assert cfg["head_dim"] * cfg["num_attention_heads"] == cfg["hidden_size"]
    # GQA: SmolLM2-135M tem 9 Q e 3 KV
    assert cfg["num_key_value_heads"] >= 1
    assert cfg["rope_theta"] is not None


def test_contagem_fecha_com_num_parameters(modelo_pequeno):
    _, model, _, _ = modelo_pequeno
    c = contar_parametros(model)
    assert c["erro_relativo"] <= 0.001
    assert c["por_componente"]["atencao"] > 0
    assert c["por_componente"]["ffn"] > 0
    assert c["por_componente"]["embedding"] > 0
    # soma dos baldes = total único
    assert sum(c["por_componente"].values()) == c["total_unico"]


def test_reconstruir_bloco_zero_bate_hidden_state(modelo_pequeno):
    tok, model, device, _ = modelo_pequeno
    ids = tok(FRASE_PADRAO, return_tensors="pt")
    input_ids = ids.input_ids.to(device)
    s = input_ids.size(1)
    position_ids = torch.arange(s, device=device).unsqueeze(0)
    with torch.no_grad():
        saida = model(
            input_ids=input_ids,
            position_ids=position_ids,
            output_hidden_states=True,
            output_attentions=True,
            use_cache=False,
        )
        x_nossa, pesos = reconstruir_bloco(
            model, saida.hidden_states[0], position_ids, camada=0
        )
    delta = (x_nossa - saida.hidden_states[1]).abs().max().item()
    assert delta < 1e-3, delta
    mapa = saida.attentions[0][0, 0]
    assert (mapa.triu(1) < 1e-6).all()
    assert (pesos[0, 0].triu(1) < 1e-6).all()
    assert torch.allclose(pesos, saida.attentions[0], atol=1e-5)


def test_gqa_projecoes_k_menores_que_q(modelo_pequeno):
    _, model, _, _ = modelo_pequeno
    cfg = ler_config(model)
    layer = model.model.layers[0]
    d = cfg["hidden_size"]
    assert layer.self_attn.q_proj.out_features == d
    if cfg["gqa"]:
        esperado_kv = cfg["num_key_value_heads"] * cfg["head_dim"]
        assert layer.self_attn.k_proj.out_features == esperado_kv
        assert layer.self_attn.v_proj.out_features == esperado_kv
        assert layer.self_attn.k_proj.out_features < d
