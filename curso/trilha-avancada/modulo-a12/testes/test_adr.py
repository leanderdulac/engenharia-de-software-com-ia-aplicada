from pathlib import Path

ADR = Path(__file__).resolve().parents[1] / "adr-capstone.md"


def test_adr_tem_secoes_obrigatorias():
    t = ADR.read_text(encoding="utf-8")
    for h in ("# ADR", "## Contexto", "## Decisão 1", "## Decisão 2", "## Alternativa rejeitada", "C09.5"):
        assert h in t, h
    assert "decisoes-de-arquitetura.md" in t
    assert "copia" in t.lower()
