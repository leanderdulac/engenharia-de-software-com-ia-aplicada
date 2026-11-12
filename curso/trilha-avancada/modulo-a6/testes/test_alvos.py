from alvos_lora import ALVOS, cfg
from gguf_status import status


def test_alvos_sao_subconjuntos():
    assert set(ALVOS["qv"]) <= set(ALVOS["attn"]) <= set(ALVOS["all_linear"])
    assert set(ALVOS["mlp"]).isdisjoint(ALVOS["attn"])
    c = cfg(ALVOS["qv"])
    assert c.r == 8
    assert c.lora_dropout == 0.0


def test_gguf_declara_nao_calibrado():
    s = status()
    assert s["status"] == "nao_calibrado"
    assert "gguf" in s["nota"].lower() or "Ollama" in s["nota"] or "ollama" in s["nota"]
