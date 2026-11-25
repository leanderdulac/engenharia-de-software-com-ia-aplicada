"""QAT de brinquedo vs PTQ no mesmo MLP — sem MiniGPT do A3.

Fake-quant INT8 com straight-through estimator (Jacob et al. 2018). Tarefa: regressão
``y = sin(x)`` em 1-D expandido. Rápido em CPU.
"""

from __future__ import annotations

from typing import Any

import torch
from torch import nn
import torch.nn.functional as F


def fake_quant_int8_ste(w: torch.Tensor) -> torch.Tensor:
    scale = w.detach().abs().amax().clamp(min=1e-8) / 127.0
    w_s = w / scale
    q = w_s.round().clamp(-127, 127)
    # STE: gradiente ignora o round
    q_ste = w_s + (q - w_s).detach()
    return q_ste * scale


class MLP(nn.Module):
    def __init__(self, d: int = 32, qat: bool = False):
        super().__init__()
        self.l1 = nn.Linear(1, d)
        self.l2 = nn.Linear(d, 1)
        self.qat = qat

    def _w(self, linear: nn.Linear) -> tuple[torch.Tensor, torch.Tensor | None]:
        w, b = linear.weight, linear.bias
        if self.qat:
            w = fake_quant_int8_ste(w)
            if b is not None:
                b = fake_quant_int8_ste(b)
        return w, b

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w1, b1 = self._w(self.l1)
        w2, b2 = self._w(self.l2)
        h = F.relu(F.linear(x, w1, b1))
        return F.linear(h, w2, b2)


def _dados(n: int, g: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    x = (torch.rand(n, 1, generator=g) * 6.28) - 3.14
    y = torch.sin(x)
    return x, y


def _treinar(modelo: MLP, passos: int, g: torch.Generator, lr: float = 1e-2) -> float:
    opt = torch.optim.Adam(modelo.parameters(), lr=lr)
    modelo.train()
    perda_last = 0.0
    for _ in range(passos):
        x, y = _dados(256, g)
        perda = F.mse_loss(modelo(x), y)
        opt.zero_grad(set_to_none=True)
        perda.backward()
        opt.step()
        perda_last = float(perda.detach())
    return perda_last


@torch.no_grad()
def mse_heldout(modelo: MLP, g: torch.Generator, n: int = 512) -> float:
    modelo.eval()
    x, y = _dados(n, g)
    return float(F.mse_loss(modelo(x), y))


def aplicar_ptq_int8(modelo: MLP) -> None:
    with torch.no_grad():
        for lin in (modelo.l1, modelo.l2):
            lin.weight.data.copy_(fake_quant_int8_ste(lin.weight.data))
            if lin.bias is not None:
                lin.bias.data.copy_(fake_quant_int8_ste(lin.bias.data))


def comparar_ptq_qat(*, passos: int = 400, semente: int = 0) -> dict[str, Any]:
    g = torch.Generator().manual_seed(semente)
    torch.manual_seed(semente)

    fp = MLP(qat=False)
    _treinar(fp, passos, g)
    mse_fp = mse_heldout(fp, torch.Generator().manual_seed(semente + 1))

    ptq = MLP(qat=False)
    ptq.load_state_dict(fp.state_dict())
    aplicar_ptq_int8(ptq)
    mse_ptq = mse_heldout(ptq, torch.Generator().manual_seed(semente + 1))

    g2 = torch.Generator().manual_seed(semente)
    qat = MLP(qat=True)
    _treinar(qat, passos, g2)
    qat.qat = True
    mse_qat = mse_heldout(qat, torch.Generator().manual_seed(semente + 1))

    return {
        "passos": passos,
        "mse_fp32": mse_fp,
        "mse_ptq_depois": mse_ptq,
        "mse_qat": mse_qat,
        "qat_melhor_que_ptq": mse_qat < mse_ptq,
        "ptq_pior_que_fp32": mse_ptq > mse_fp,
    }
