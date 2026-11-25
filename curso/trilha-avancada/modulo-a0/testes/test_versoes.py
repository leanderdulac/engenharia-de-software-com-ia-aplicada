from versoes import orcamento_memoria, versao
from bancada_latencia import p50_dentro_de


def test_torch_transformers_presentes():
    assert versao("torch")
    assert versao("transformers")
    assert versao("peft")


def test_orcamento_pesos_mais_adam():
    o = orcamento_memoria(1_000_000, 4)
    assert o["pesos_mb"] == 4.0
    assert o["grad_mb"] == 4.0
    assert o["adam_mb"] == 8.0
    assert o["total_treino_mb"] == 16.0


def test_p50_tolerancia():
    assert p50_dentro_de(1.0, 1.15, tol=0.20)
    assert not p50_dentro_de(1.0, 1.5, tol=0.20)
