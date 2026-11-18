from pathlib import Path

TRILHA = Path(__file__).resolve().parents[2]


def test_licenca_todos_os_direitos_reservados():
    lic = TRILHA / "LICENSE.md"
    pendente = TRILHA / "LICENSE-PENDENTE.md"
    assert lic.is_file(), "LICENSE.md da trilha precisa existir"
    assert not pendente.exists(), "LICENSE-PENDENTE.md foi substituído; não republicar"
    t = lic.read_text(encoding="utf-8")
    assert "Todos os direitos reservados" in t
    assert "Leandro França de Mello" in t
    assert "2026" in t
    assert "NOTICE.md" in t
    idx = (TRILHA / "README.md").read_text(encoding="utf-8")
    assert "LICENSE.md" in idx
    assert "LICENSE-PENDENTE" not in idx
    notice = (TRILHA / "NOTICE.md").read_text(encoding="utf-8")
    assert "LICENSE.md" in notice
    assert "LICENSE-PENDENTE" not in notice


def test_trilha_nao_cita_licenca_pendente():
    """Referências antigas ao arquivo pendente não podem voltar em outros módulos."""
    este = Path(__file__).resolve()
    restos = []
    for path in TRILHA.rglob("*"):
        if not path.is_file() or path.resolve() == este:
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".txt"}:
            continue
        texto = path.read_text(encoding="utf-8", errors="replace")
        if "LICENSE-PENDENTE" in texto:
            restos.append(str(path.relative_to(TRILHA)))
    assert restos == [], "ainda citam LICENSE-PENDENTE.md: " + ", ".join(restos)
