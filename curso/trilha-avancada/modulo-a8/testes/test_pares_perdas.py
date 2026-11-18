from __future__ import annotations

import torch

from pares import (
    estatistica_comprimento,
    pares_avaliacao,
    pares_dpo,
    pares_kto,
    pares_treino,
    split_ok,
)
from perdas import exemplo_numerico_aula, perda_dpo, perda_ipo, tabela_no_lote


def test_pares_nao_vazios_e_rejeitado_mais_longo():
    p = pares_dpo()
    assert len(p) >= 8
    for ex in p:
        assert "prompt" in ex and "chosen" in ex and "rejected" in ex
        assert ex["chosen"] != ex["rejected"]
        assert ex["prompt"].endswith("\n")
        assert not ex["chosen"].startswith("\n")
        assert not ex["rejected"].startswith("\n")
        assert not ex["prompt"].rstrip().endswith('":')
    c = estatistica_comprimento(p)
    assert c["rejeitado_mais_longo"]
    kto = pares_kto()
    assert len(kto) == 2 * len(pares_treino())
    assert {x["label"] for x in kto} == {True, False}


def test_treino_e_eval_disjuntos():
    sp = split_ok()
    assert sp["n_treino"] >= 8
    assert sp["n_eval"] >= 3
    assert sp["prompts_disjuntos"]
    tr = {p["prompt"] for p in pares_treino()}
    ev = {p["prompt"] for p in pares_avaliacao()}
    assert tr.isdisjoint(ev)


def test_pares_originais_nao_citam_arquivo_m09():
    blob = " ".join(f"{x['prompt']} {x['chosen']} {x['rejected']}" for x in pares_dpo())
    assert "preference-dataset-amplitude" not in blob
    assert "Marcos Nogueira" not in blob  # nomes do JSONL do M09, nao os nossos


def test_dpo_menor_quando_chosen_ganha():
    w = torch.tensor([-1.0, -1.0])
    l = torch.tensor([-5.0, -5.0])
    wr = torch.tensor([-2.0, -2.0])
    lr = torch.tensor([-2.0, -2.0])
    boa = perda_dpo(w, l, wr, lr, beta=0.1)
    ruim = perda_dpo(l, w, wr, lr, beta=0.1)
    assert boa < ruim


def test_ipo_e_tabela_finitas():
    ex = exemplo_numerico_aula()
    assert ex["dpo_sigmoid"] > 0
    assert ex["ipo"] >= 0
    assert ex["simpo"] > 0
    w = torch.tensor([-2.0])
    l = torch.tensor([-2.0])
    # h=0 → IPO = (0 - 1/(2β))²
    ipo = perda_ipo(w, l, w, l, beta=0.5)
    assert abs(float(ipo) - (1.0) ** 2) < 1e-5  # 1/(2*0.5)=1


def test_dpo_vs_beta_cai_quando_margem_positiva():
    w = torch.tensor([-1.0])
    l = torch.tensor([-4.0])
    wr = torch.tensor([-2.0])
    lr = torch.tensor([-2.0])
    # h = 3 > 0 → β maior satura σ e a perda cai (mesmos logps, sem retreino)
    l01 = float(perda_dpo(w, l, wr, lr, beta=0.1))
    l05 = float(perda_dpo(w, l, wr, lr, beta=0.5))
    l10 = float(perda_dpo(w, l, wr, lr, beta=1.0))
    assert l01 > l05 > l10 > 0


def test_tabela_marca_experimental():
    t = tabela_no_lote(
        torch.tensor([-1.0]),
        torch.tensor([-2.0]),
        torch.tensor([-1.1]),
        torch.tensor([-1.2]),
        torch.tensor([4.0]),
        torch.tensor([8.0]),
    )
    assert "experimental" in t["apis"]["orpo"]
    assert "experimental" in t["apis"]["simpo"]
    assert "estavel" in t["apis"]["dpo_sigmoid"]
    assert t["nao_e_ranking"] is True
