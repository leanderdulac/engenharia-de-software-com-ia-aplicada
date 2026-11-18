from pathlib import Path

TRILHA = Path(__file__).resolve().parents[2]
AULA = TRILHA / "modulo-a14" / "aula.md"


def test_leituras_e_notice():
    lei = (TRILHA / "leituras.md").read_text(encoding="utf-8")
    assert "smlbook.org" in lei
    assert "9781108843607" in lei
    assert "4/mar/2026" in lei or "4/mar/2026" in lei.replace("março", "mar")
    assert "statlearning.com" in lei
    assert "1611.03530" in lei
    n = (TRILHA / "NOTICE.md").read_text(encoding="utf-8")
    assert "smlbook.org" in n
    assert "derivad" in n.lower()
    assert "PDF" in n and "não" in n.lower()


def test_aula_nao_e_o_livro():
    t = AULA.read_text(encoding="utf-8")
    assert "não" in t.lower() and "parafraseia" in t
    assert "Expected new data error" not in t
    assert "sml-book-draft" not in t
    pdfs = list((TRILHA / "modulo-a14").rglob("*.pdf"))
    assert pdfs == []


def test_indice_tem_a14():
    idx = (TRILHA / "README.md").read_text(encoding="utf-8")
    assert "modulo-a14/README.md" in idx
    assert "leituras.md" in idx
