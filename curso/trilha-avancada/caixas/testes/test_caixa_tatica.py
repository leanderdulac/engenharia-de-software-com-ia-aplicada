"""Caixa tática × estratégica: texto, índices e a simulação offline."""

from __future__ import annotations

import importlib.util
import inspect
import json
import re
from pathlib import Path

CAIXAS = Path(__file__).resolve().parents[1]
TRILHA = CAIXAS.parent
CAIXA = CAIXAS / "programacao-tatica-vs-estrategica.md"
LAB = CAIXAS / "tatica" / "lab" / "simular.py"
JSON_MED = CAIXAS / "tatica" / "execucao" / "medicao.json"

MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _carregar():
    spec = importlib.util.spec_from_file_location("simular_tatica", LAB)
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


def test_caixa_cita_a_medicao_e_a_tese():
    t = CAIXA.read_text(encoding="utf-8")
    for trecho in (
        "lei de Goodhart",
        "autor do curso",
        "nao_calibrado",
        "revisor_design",
        "streaming",
        "A12",
        "A14",
    ):
        assert trecho in t, trecho
    d = json.loads(JSON_MED.read_text(encoding="utf-8"))
    for modo in ("A", "B", "C"):
        for chave in (
            "entregues_teste_verde",
            "violacoes",
            "duplicacao",
            "custo_feature_seguinte",
            "atalhos_tentados",
            "atalhos_aceitos",
        ):
            assert str(d[modo][chave]["media"]) in t
            assert str(d[modo][chave]["desvio_amostral"]) in t


def test_revisor_nao_recebe_o_teste():
    mod = _carregar()
    params = tuple(inspect.signature(mod.revisor_design).parameters)
    assert params == ("tipo", "trecho")
    assert mod.medir()["revisor_ve_testes"] is False


def test_simulacao_bate_com_o_json_e_com_a_tese():
    mod = _carregar()
    fresco = mod.medir()
    assert fresco == mod.medir()
    gravado = json.loads(JSON_MED.read_text(encoding="utf-8"))
    assert fresco == gravado
    assert fresco["simulacao"] is True
    assert fresco["llm_real"] == "nao_calibrado"
    assert fresco["n_seeds"] >= 20
    assert fresco["n_features"] == 8
    for i, linha_a in enumerate(fresco["A"]["por_seed"]):
        linha_b = fresco["B"]["por_seed"][i]
        linha_c = fresco["C"]["por_seed"][i]
        assert linha_a["entregues_teste_verde"] == 8
        assert linha_b["entregues_teste_verde"] == 8
        assert linha_c["entregues_teste_verde"] == 8
        assert linha_a["violacoes"] == linha_b["violacoes"]
        assert linha_b["duplicacao"] >= linha_a["duplicacao"]
        assert linha_c["violacoes"] == 0
        assert linha_c["atalhos_aceitos"] == 0
        assert linha_c["custo_feature_seguinte"] == 4
        assert linha_a["disparos_regra"] == 0
        assert linha_a["atalhos_tentados"] == linha_c["atalhos_tentados"]
    assert fresco["B"]["duplicacao"]["media"] > fresco["A"]["duplicacao"]["media"]
    assert fresco["B"]["passos"]["media"] > fresco["A"]["passos"]["media"]
    assert fresco["C"]["escalados"]["media"] > 0


def test_links_indice():
    t = CAIXA.read_text(encoding="utf-8")
    faltando = [str(p) for p in _relativos(t, CAIXA) if not p.exists()]
    assert faltando == []
    trilha = (TRILHA / "README.md").read_text(encoding="utf-8")
    caixas = (CAIXAS / "README.md").read_text(encoding="utf-8")
    assert "caixas/programacao-tatica-vs-estrategica.md" in trilha
    assert "programacao-tatica-vs-estrategica.md" in caixas
