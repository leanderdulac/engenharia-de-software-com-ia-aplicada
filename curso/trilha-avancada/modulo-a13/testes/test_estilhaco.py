from estilhaco import P3, P4, Y_XOR, dicotomias, xor_falha
from frases_dominio import split_ok
from limite_vc import ponte_a5, termo_aditivo, vacuo


def test_tres_pontos_estilhacam():
    d = dicotomias(P3)
    assert d["n_dicotomias"] == 8
    assert d["n_separaveis"] == 8
    assert d["estilhaça"] is True


def test_quatro_pontos_xor_falha():
    d = dicotomias(P4)
    assert d["estilhaça"] is False
    assert list(Y_XOR) in d["falhas"] or [1 - x for x in Y_XOR] in d["falhas"]
    x = xor_falha()
    assert x["linearmente_separavel"] is False


def test_limite_vacuo_h_maior_que_n():
    v = vacuo(460_800, 4)
    assert v["vacuo"] is True
    assert v["termo"] == "inf"


def test_limite_vc3_n4_ainda_vacuo():
    # h=3 < n=4, mas o termo √ ainda ≥ 1
    eps = termo_aditivo(3, 4)
    assert eps >= 1.0
    assert vacuo(3, 4)["vacuo"] is True


def test_limite_n_grande_nao_vacuo():
    v = vacuo(3, 10_000)
    assert v["vacuo"] is False
    assert isinstance(v["termo"], float)
    assert v["termo"] < 0.2


def test_ponte_a5_numeros_publicados():
    p = ponte_a5()
    assert p["acc_treino_a5"] == 1.0
    assert p["acc_eval_a5"] == 0.5
    assert p["n_treino"] == 4
    assert p["termo_lora"]["vacuo"] is True
    assert "não é a teoria" in p["leitura"] or "nao e a teoria" in p["leitura"].replace("é", "e")


def test_frases_split_disjunto():
    assert split_ok()
