from __future__ import annotations

from hacking import demonstrar
from reinforce import treinar_reinforce
from tarefas import pares_avaliacao, pares_treino, recompensa_exata, recompensa_hack_digito, split_ok


def test_reinforce_aprende_acao_otima():
    r = treinar_reinforce(passos=120, semente=1, baseline=True)
    assert r["subiu"] or r["p_otima"] > 0.4
    assert r["p_otima"] > 1.0 / r["n_acoes"]
    assert r["recompensa_media_fim"] >= r["recompensa_media_inicio"] - 1e-9


def test_split_e_recompensas():
    sp = split_ok()
    assert sp["n_treino"] >= 6 and sp["n_eval"] >= 3
    assert sp["prompts_disjuntos"]
    tr, ev = pares_treino(), pares_avaliacao()
    assert {p["prompt"] for p in tr}.isdisjoint({p["prompt"] for p in ev})
    for p in tr + ev:
        assert p["prompt"].endswith("=")
        assert not p["prompt"].endswith("=\n")
        assert p["answer"].isdigit()
    assert recompensa_exata(["4\n\nA = "], ["4"]) == [1.0]
    assert recompensa_exata(["5, 4+3"], ["7"]) == [0.0]


def test_hacking_diverge_da_exata():
    d = demonstrar()
    assert d["n_divergencias"] >= 2
    assert d["exata"][0] == 1.0  # "7"
    assert d["exata"][1] == 0.0  # "0"
    assert d["hack_digito"][1] == 1.0
    assert recompensa_exata(["12"], ["7"]) == [0.0]
    assert recompensa_hack_digito(["abc"]) == [0.0]
    assert recompensa_hack_digito(["x0"]) == [1.0]
