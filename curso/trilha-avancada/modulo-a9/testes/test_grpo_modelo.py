from __future__ import annotations

import pytest
import torch


@pytest.mark.modelo
def test_gerar_eval_recompensa_no_intervalo():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from tarefas import pares_avaliacao, recompensa_exata
    from treinar_grpo import MODELO, gerar_e_pontuar

    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    model.eval()
    r = gerar_e_pontuar(model, tok, pares_avaliacao()[:2], recompensa_exata)
    assert r["n"] == 2
    assert 0.0 <= r["recompensa_media"] <= 1.0
    assert 0 <= r["n_acertos"] <= 2


@pytest.mark.modelo
def test_grpo_trainer_roda_um_passo_com_lora():
    from tarefas import pares_treino, recompensa_exata
    from treinar_grpo import treinar_grpo

    g = treinar_grpo(
        pares_treino()[:4],
        recompensa_exata,
        beta=0.0,
        max_steps=1,
        num_generations=2,
    )
    assert g["atualiza_pesos"] is True
    assert g["api"].startswith("trl.GRPOTrainer")
    assert g["train_loss"] == g["train_loss"]  # não NaN
    nomes = [n for n, p in g["trainer"].model.named_parameters() if p.requires_grad]
    assert any("lora" in n.lower() for n in nomes)
    g.pop("trainer", None)
    g.pop("tokenizer", None)
