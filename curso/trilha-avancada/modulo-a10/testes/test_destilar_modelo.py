from __future__ import annotations

import pytest
import torch


@pytest.mark.modelo
def test_loss_sequencia_finita():
    from destilar import carregar_aluno, loss_sequencia

    m, tok = carregar_aluno("cpu")
    loss = loss_sequencia(m, tok, "1+1=", "2", "cpu")
    assert torch.isfinite(loss)
    assert loss.item() == loss.item()
