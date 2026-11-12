from __future__ import annotations

from filtro import aceita, filtrar
from licencas import manifesto
from tarefas import pares_avaliacao, pares_treino, split_ok


def test_split_e_filtro():
    sp = split_ok()
    assert sp["n_treino"] >= 16 and sp["n_eval"] >= 40
    assert sp["prompts_disjuntos"]
    tr, ev = pares_treino(), pares_avaliacao()
    assert {p["prompt"] for p in tr}.isdisjoint({p["prompt"] for p in ev})
    assert aceita("6\n\nA = ", "6")
    assert not aceita("10\n", "6")
    f = filtrar(
        [
            {"prompt": "x", "answer": "7", "complecao": "7\n"},
            {"prompt": "y", "answer": "7", "complecao": "0"},
        ]
    )
    assert f["n_aceitos"] == 1 and f["n_rejeitados"] == 1


def test_licencas_apache():
    m = manifesto()
    assert m["professor"]["licenca_card"] == "Apache-2.0"
    assert m["aluno"]["licenca_card"] == "Apache-2.0"
    assert "sinteticos" in m["dados_sinteticos"].lower() or "Apache" in m["dados_sinteticos"]
