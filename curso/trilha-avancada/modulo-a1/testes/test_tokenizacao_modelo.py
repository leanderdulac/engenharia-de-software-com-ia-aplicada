from __future__ import annotations

import pytest
import torch

from amostragem import generate_greedy_hf, greedy_autorregressivo
from tokenizacao import tabela_pt_en

pytestmark = pytest.mark.modelo


def test_tabela_tres_tokenizers_e_razao_pt_en():
    tab = tabela_pt_en()
    assert tab["vocab_size"]["smollm2"] == 49152
    assert tab["vocab_size"]["qwen25"] > 100000
    assert tab["vocab_size"]["caracteres"] == 256
    assert len(tab["quebra_bpe"]["smollm2"]) >= 2  # "Segurado" não é 1 token
    for par in tab["pares"]:
        sm = par["smollm2"]
        assert sm["pt"]["n_tokens"] >= 1 and sm["en"]["n_tokens"] >= 1
        assert sm["razao_pt_en"] is not None


def test_greedy_manual_bate_com_generate(modelo_pequeno):
    tok, model, device, _ = modelo_pequeno
    prompt = "2+2="
    nossa = greedy_autorregressivo(model, tok, prompt, max_novos=6, device=device)
    hf = generate_greedy_hf(model, tok, prompt, max_novos=6, device=device)
    assert nossa["ids_novos"] == hf["ids_novos"]


def test_embedding_e_uma_linha_por_id(modelo_pequeno):
    tok, model, _, _ = modelo_pequeno
    e = model.model.embed_tokens.weight
    assert e.shape[0] == model.config.vocab_size
    ids = tok("Ana", add_special_tokens=False).input_ids
    assert len(ids) >= 1
    vec = e[ids[0]]
    assert vec.shape[-1] == model.config.hidden_size
    assert torch.isfinite(vec).all()
