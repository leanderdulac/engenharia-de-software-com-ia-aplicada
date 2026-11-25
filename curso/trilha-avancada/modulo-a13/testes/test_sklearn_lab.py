from classificar_frases import tabela
from margem_c import curva_c
from rotulos_aleatorios import experimento


def test_curva_c_tem_cinco_pontos():
    c = curva_c()
    assert len(c["linhas"]) == 5
    for lin in c["linhas"]:
        assert lin["n_sv"] >= 2
        assert lin["margem"] is not None and lin["margem"] > 0


def test_c_pequeno_margem_maior_que_c_grande():
    linhas = {lin["C"]: lin for lin in curva_c()["linhas"]}
    assert linhas[0.01]["margem"] > linhas[100.0]["margem"]


def test_tfidf_svm_vs_logreg_sem_modelo():
    t = tabela(tentar_embed=False)
    assert t["encoder_principal"] == "tfidf"
    assert t["embeddings"]["usou"] is False
    for nome in ("svm_linear", "svm_rbf", "logreg"):
        bloco = t["tfidf"][nome]
        assert 0.0 <= bloco["acc_treino"] <= 1.0
        assert 0.0 <= bloco["acc_eval"] <= 1.0


def test_rotulos_aleatorios_mlp_interpola():
    e = experimento()
    assert e["fracao_rotulos_trocados"] > 0
    # rede e RBF têm capacidade de decorar o treino embaralhado
    assert e["rotulos_aleatorios"]["mlp"]["acc_treino"] == 1.0
    assert e["rotulos_aleatorios"]["svm_rbf"]["acc_treino"] == 1.0
    # eval nos rótulos verdadeiros não herda a decoração
    assert e["rotulos_aleatorios"]["mlp"]["acc_eval"] <= 0.75
    assert e["rotulos_aleatorios"]["svm_rbf"]["acc_eval"] <= 0.75
