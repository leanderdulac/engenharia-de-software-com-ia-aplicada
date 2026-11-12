from aritmetica import motivo_errado, split_ok, voto


def test_voto_maioria():
    v = voto(["Resposta: 7", "7", "Resposta: 9"])
    assert v["voto"] == "7"
    assert v["n"] == 2


def test_motivo_errado_e_split():
    assert split_ok()
    assert motivo_errado("Resposta: 9", 4, 5, 9, "9")
    assert not motivo_errado("4+5=9 Resposta: 9", 4, 5, 9, "9")
    assert not motivo_errado("Resposta: 8", 4, 5, 9, "8")
