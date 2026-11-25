"""Checagens locais da caixa /teamwork: ficheiro, âncoras e links relativos."""

from __future__ import annotations

import re
from pathlib import Path

CAIXAS = Path(__file__).resolve().parents[1]
TRILHA = CAIXAS.parent
CAIXA = CAIXAS / "antigravity-teamwork.md"
README_CAIXAS = CAIXAS / "README.md"
README_TRILHA = TRILHA / "README.md"
NOTICE = TRILHA / "NOTICE.md"

MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _relativos(texto: str, origem: Path) -> list[tuple[str, Path]]:
    out = []
    for _, alvo in MD_LINK.findall(texto):
        url = alvo.strip()
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        url = url.split("#", 1)[0]
        if not url:
            continue
        out.append((alvo, (origem.parent / url).resolve()))
    return out


def test_caixa_existe_e_tem_secoes():
    t = CAIXA.read_text(encoding="utf-8")
    for trecho in (
        "falsificador",
        "Zircon",
        "libgav1",
        "DuoDiscover",
        "yardstick",
        "Kendall",
        "A7",
        "A12",
        "A13",
        "M09",
        "Não há endosso",
        "não modificada",
        "/boost",
    ):
        assert trecho in t, trecho
    assert "800" in t and "170" in t
    assert "4,09" in t or "4.09" in t
    assert "23 s" in t or "23s" in t


def test_fontes_citadas_com_data():
    t = CAIXA.read_text(encoding="utf-8")
    assert "research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature" in t
    assert "x.com/mirrokni/status/2121351383236436247" in t
    assert "13/11/2026" in t


def test_aviso_nao_reproduz():
    t = CAIXA.read_text(encoding="utf-8").lower()
    assert "replicou" in t or "reproduz" in t
    assert "endosso" in t


def test_links_relativos_da_caixa_existem():
    t = CAIXA.read_text(encoding="utf-8")
    faltando = [str(p) for _, p in _relativos(t, CAIXA) if not p.exists()]
    assert faltando == []


def test_indice_aponta_a_caixa():
    idx = README_TRILHA.read_text(encoding="utf-8")
    assert "caixas/antigravity-teamwork.md" in idx
    assert "30 min" in idx
    assert README_CAIXAS.is_file()
    assert "antigravity-teamwork.md" in README_CAIXAS.read_text(encoding="utf-8")


def test_notice_regista_google_research():
    n = NOTICE.read_text(encoding="utf-8")
    assert "Antigravity" in n
    assert "research.google" in n
