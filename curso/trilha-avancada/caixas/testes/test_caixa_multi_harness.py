"""Caixa multi-harness: texto, índices e a simulação offline."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

CAIXAS = Path(__file__).resolve().parents[1]
TRILHA = CAIXAS.parent
CAIXA = CAIXAS / "multi-harness.md"
LAB = CAIXAS / "multi" / "lab" / "simular.py"
JSON_MED = CAIXAS / "multi" / "execucao" / "medicao.json"

MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _carregar():
    spec = importlib.util.spec_from_file_location("simular_multi", LAB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _relativos(texto: str, origem: Path) -> list[Path]:
    out = []
    for _, alvo in MD_LINK.findall(texto):
        url = alvo.strip()
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        url = url.split("#", 1)[0]
        if not url:
            continue
        out.append((origem.parent / url).resolve())
    return out


def test_caixa_cita_a_medicao():
    t = CAIXA.read_text(encoding="utf-8")
    for trecho in (
        "falsificador",
        "teste congelado",
        "corrida",
        "nao_calibrado",
        "PROGRESS",
        "A14",
    ):
        assert trecho in t, trecho
    d = json.loads(JSON_MED.read_text(encoding="utf-8"))
    for modo in ("U", "T"):
        for chave in (
            "defeitos_que_escapam",
            "escritas_teste_barradas",
            "passagens",
            "passos",
            "escalados",
        ):
            assert str(d[modo][chave]["media"]) in t
            assert str(d[modo][chave]["desvio_amostral"]) in t


def test_simulacao_bate_com_o_json():
    mod = _carregar()
    fresco = mod.medir()
    assert fresco == mod.medir()
    gravado = json.loads(JSON_MED.read_text(encoding="utf-8"))
    assert fresco == gravado
    assert fresco["simulacao"] is True
    assert fresco["llm_real"] == "nao_calibrado"
    assert fresco["n_seeds"] >= 20
    assert fresco["n_tarefas"] == 6
    for i, unico in enumerate(fresco["U"]["por_seed"]):
        trio = fresco["T"]["por_seed"][i]
        assert unico["escritas_teste_barradas"] == 0
        assert trio["escritas_teste_aplicadas"] == 0
        assert trio["escritas_teste_barradas"] == trio["tentativas_escrita_teste"]
        assert trio["teste_permaneceu_congelado"] is True
        assert unico["passagens"] == 0
        assert trio["defeitos_que_escapam"] <= unico["defeitos_que_escapam"]
        assert trio["passos"] > unico["passos"]
    assert fresco["T"]["defeitos_que_escapam"]["media"] < fresco["U"]["defeitos_que_escapam"]["media"]
    assert fresco["T"]["defeitos_que_escapam"]["media"] > 0


def test_links_indice_e_contratos():
    t = CAIXA.read_text(encoding="utf-8")
    faltando = [str(p) for p in _relativos(t, CAIXA) if not p.exists()]
    assert faltando == []
    for nome in (
        "CONTRACT-produtor.md",
        "CONTRACT-revisor.md",
        "CONTRACT-falsificador.md",
        "PROGRESS.md",
    ):
        texto = (CAIXAS / "multi" / "templates" / nome).read_text(encoding="utf-8")
        assert "goal:" in texto or nome == "PROGRESS.md"
    trilha = (TRILHA / "README.md").read_text(encoding="utf-8")
    caixas = (CAIXAS / "README.md").read_text(encoding="utf-8")
    assert "caixas/multi-harness.md" in trilha
    assert "multi-harness.md" in caixas
