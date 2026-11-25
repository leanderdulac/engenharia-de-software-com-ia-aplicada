from curvas import knn, polinomio
from ic_binomial import A5_EVAL, bootstrap_seq, ponte_historico, wilson
from interpolar import curva_features
from vazamento import duplicatas_no_teste, escala_antes_vs_depois, kfold_variabilidade


def test_wilson_n2_quase_vazio():
    w = wilson(1, 2)
    assert w["p"] == 0.5
    assert w["largura"] >= 0.5
    assert 0.0 <= w["lo"] < 0.5 < w["hi"] <= 1.0


def test_wilson_n6_ainda_largo():
    w = wilson(3, 6)
    assert w["largura"] > 0.5
    assert w["lo"] < 0.5 < w["hi"]


def test_bootstrap_deterministico():
    a = bootstrap_seq(3, 8, semente=0)
    b = bootstrap_seq(3, 8, semente=0)
    assert a == b
    assert a["largura"] > 0


def test_ponte_usa_numeros_publicados():
    p = ponte_historico()
    assert p["a5_eval_n2"]["n"] == A5_EVAL["n"] == 2
    assert p["a5_eval_n2"]["k"] == 1
    assert p["a7_direto_n8"]["n"] == 8
    assert p["a7_direto_n8"]["k"] == 3
    assert p["a13_zhang_svm_n6"]["n"] == 6
    assert p["a5_eval_n2"]["vacuo_pratico"] is True
    assert "hipotese" in p["a5_se_n6"]["origem"] or "hipótese" in p["a5_se_n6"]["origem"]


def test_duplicata_otimista():
    d = duplicatas_no_teste()
    assert d["otimista"] is True
    assert d["acc_holdout_com_duplicata"] > d["acc_holdout_limpo"]


def test_kfold_cinco_dobras():
    k = kfold_variabilidade()
    assert len(k["accs"]) == 5
    assert k["desvio"] >= 0.0
    assert min(k["accs"]) <= max(k["accs"])


def test_escala_campos():
    e = escala_antes_vs_depois()
    assert 0.0 <= e["acc_escala_antes_do_split"] <= 1.0
    assert 0.0 <= e["acc_escala_so_treino"] <= 1.0


def test_poli_treino_cai_com_grau():
    p = polinomio()
    mse1 = next(ln["mse_treino"] for ln in p["linhas"] if ln["grau"] == 1)
    mse16 = next(ln["mse_treino"] for ln in p["linhas"] if ln["grau"] == 16)
    assert mse16 < mse1


def test_knn_k1_decora_mais_que_k21():
    t = knn()
    a1 = next(ln["acc_treino"] for ln in t["linhas"] if ln["k"] == 1)
    a21 = next(ln["acc_treino"] for ln in t["linhas"] if ln["k"] == 21)
    assert a1 >= a21


def test_features_tem_pico():
    c = curva_features()
    assert 36 <= c["pico_p"] <= 44
    assert len(c["linhas"]) >= 6
    assert all("mse_eval" in ln for ln in c["linhas"])


def test_selectkbest_campos_e_duplicata():
    e = escala_antes_vs_depois()
    assert e["otimista"] is True
    assert "SelectKBest" in e["mecanismo"]
