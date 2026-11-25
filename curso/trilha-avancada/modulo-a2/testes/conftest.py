from __future__ import annotations

import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[1] / "lab"
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))


@pytest.fixture(scope="session")
def modelo_pequeno():
    """Carrega SmolLM2 (ou TRILHA_A2_MODELO) uma vez por sessão de testes."""
    from inspecionar_modelo import carregar, id_do_modelo

    tok, model, device = carregar()
    return tok, model, device, id_do_modelo()
