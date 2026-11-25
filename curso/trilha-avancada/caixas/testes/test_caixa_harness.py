"""Checagens da caixa de harness: texto, índices e a simulação offline."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CAIXAS = Path(__file__).resolve().parents[1]
TRILHA = CAIXAS.parent
CAIXA = CAIXAS / "harness-engineering.md"
LAB = CAIXAS / "harness" / "lab"
JSON_MED = CAIXAS / "harness" / "execucao" / "medicao.json"
README_CAIXAS = CAIXAS / "README.md"
README_TRILHA = TRILHA / "README.md"
NOTICE = TRILHA / "NOTICE.md"

sys.path.insert(0, str(LAB))

import simular  # noqa: E402

MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


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


def test_caixa_existe_e_tem_secoes():
    t = CAIXA.read_text(encoding="utf-8")
    for trecho in (
        "Um prompt é um pedido",
        "CONTRATO",
        "AGENTS.md",
        "PROGRESS.md",
        "EXIT",
        "SENSORES",
        "MUROS",
        "A4",
        "A5",
        "A7",
        "A12",
        "A13",
        "A14",
        "M09",
        "nao_calibrado",
        "ilustrativo",
        "simulação",
        "3.2",
        "10.1",
        "0.7678",
        "0.8522",
    ):
        assert trecho in t, trecho
    assert "Não há endosso" in t or "não é endosso" in t


def test_nao_repete_alegacao_de_video():
    t = CAIXA.read_text(encoding="utf-8").lower()
    assert "engenheira sênior" not in t
    assert "engenheira senior" not in t
    assert "senior anthropic" not in t


def test_fontes_com_url_real():
    t = CAIXA.read_text(encoding="utf-8")
    for url in (
        "https://x.com/0xTrackmind/status/2124105677748527453",
        "https://www.anthropic.com/research/effective-harnesses-for-long-running-agents",
        "https://www.anthropic.com/research/harness-design-long-running-apps",
        "https://openai.com/index/harness-engineering/",
    ):
        assert url in t, url
    assert "21/11/2026" in t
    assert "26/11/2025" in t
    assert "24/03/2026" in t
    assert "11/02/2026" in t


def test_templates_tem_os_campos():
    contrato = (CAIXAS / "harness" / "templates" / "CONTRACT.md").read_text(encoding="utf-8")
    for campo in ("goal:", "output:", "scope:", "never:", "done_when:"):
        assert campo in contrato
    agents = (CAIXAS / "harness" / "templates" / "AGENTS.md").read_text(encoding="utf-8")
    assert "arquitetura.md" in agents
    progresso = (CAIXAS / "harness" / "templates" / "PROGRESS.md").read_text(encoding="utf-8")
    for secao in ("done", "current", "decisions", "dead ends", "blocked"):
        assert secao in progresso
    saida = (CAIXAS / "harness" / "templates" / "EXIT.md").read_text(encoding="utf-8")
    assert "duas vezes" in saida
    assert "escalar" in saida


def test_links_relativos_existem():
    faltando = []
    for origem in (
        CAIXA,
        CAIXAS / "harness" / "templates" / "AGENTS.md",
        CAIXAS / "harness" / "docs" / "arquitetura.md",
    ):
        texto = origem.read_text(encoding="utf-8")
        faltando.extend(str(p) for p in _relativos(texto, origem) if not p.exists())
    assert faltando == []


def test_indices_e_notice():
    trilha = README_TRILHA.read_text(encoding="utf-8")
    assert "caixas/harness-engineering.md" in trilha
    caixas = README_CAIXAS.read_text(encoding="utf-8")
    assert "harness-engineering.md" in caixas
    notice = NOTICE.read_text(encoding="utf-8")
    assert "2124105677748527453" in notice
    assert "Harness engineering" in notice or "harness engineering" in notice.lower()


def test_simulacao_deterministica_e_bate_com_o_json():
    fresco = simular.medir()
    de_novo = simular.medir()
    assert fresco == de_novo
    gravado = json.loads(JSON_MED.read_text(encoding="utf-8"))
    assert fresco == gravado
    assert fresco["simulacao"] is True
    assert fresco["llm_real"] == "nao_calibrado"
    assert fresco["artigo_40_endpoints"] == "ilustrativo_nao_medido"
    assert fresco["n_funcoes"] == 12
    assert fresco["n_seeds"] == 20


def test_modo_a_mente_modo_b_ouve_o_sensor():
    d = simular.medir()
    for linha in d["A"]["por_seed"]:
        assert linha["relatado"] == 12
        assert linha["relatado"] > linha["concluidas"]
        assert linha["testes_rodados"] is False
        assert linha["violacoes_escopo_aplicadas"] >= 0
    for linha in d["B"]["por_seed"]:
        assert linha["relatado"] == linha["concluidas"]
        assert linha["violacoes_escopo_aplicadas"] == 0
        assert linha["testes_rodados"] is True
        assert linha["escalados"] >= 1
    assert d["B"]["concluidas"]["media"] > d["A"]["concluidas"]["media"]
    assert d["A"]["concluidas"]["media"] == 3.2
    assert d["A"]["concluidas"]["desvio_amostral"] == 0.7678
    assert d["B"]["concluidas"]["media"] == 10.1
    assert d["B"]["concluidas"]["desvio_amostral"] == 0.8522
    assert d["B"]["violacoes_escopo_aplicadas"]["media"] == 0.0
