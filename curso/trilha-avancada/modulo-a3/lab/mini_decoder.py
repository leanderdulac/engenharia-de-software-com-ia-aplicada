"""Mini-decoder original da trilha (não é o MiniGPT do llm-course).

Pre-norm, atenção causal via SDPA, MLP GELU, weight tying.
Cabem poucos milhões — nesta receita ~50k parâmetros.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class MiniCfg:
    vocab: int = 32
    d: int = 32
    n_camadas: int = 2
    n_heads: int = 4
    bloco: int = 16


class MiniDecoder(nn.Module):
    def __init__(self, cfg: MiniCfg | None = None):
        super().__init__()
        self.cfg = cfg or MiniCfg()
        c = self.cfg
        assert c.d % c.n_heads == 0
        self.emb = nn.Embedding(c.vocab, c.d)
        self.camadas = nn.ModuleList([_Bloco(c) for _ in range(c.n_camadas)])
        self.norm = nn.LayerNorm(c.d)
        self.lm = nn.Linear(c.d, c.vocab, bias=False)
        self.lm.weight = self.emb.weight

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        x = self.emb(ids) * math.sqrt(self.cfg.d)
        for bloco in self.camadas:
            x = bloco(x)
        return self.lm(self.norm(x))

    def n_params(self) -> int:
        visto: set[int] = set()
        n = 0
        for p in self.parameters():
            if id(p) in visto:
                continue
            visto.add(id(p))
            n += p.numel()
        return n


class _Bloco(nn.Module):
    def __init__(self, cfg: MiniCfg):
        super().__init__()
        self.n1 = nn.LayerNorm(cfg.d)
        self.n2 = nn.LayerNorm(cfg.d)
        self.qkv = nn.Linear(cfg.d, 3 * cfg.d, bias=False)
        self.o = nn.Linear(cfg.d, cfg.d, bias=False)
        self.fc1 = nn.Linear(cfg.d, 4 * cfg.d)
        self.fc2 = nn.Linear(4 * cfg.d, cfg.d)
        self.h = cfg.n_heads
        self.hd = cfg.d // cfg.n_heads

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, s, d = x.shape
        h, hd = self.h, self.hd
        qkv = self.qkv(self.n1(x)).view(b, s, 3, h, hd).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        y = self.o(y.transpose(1, 2).contiguous().view(b, s, d))
        x = x + y
        x = x + self.fc2(F.gelu(self.fc1(self.n2(x))))
        return x


def ce_proximo_token(logits: torch.Tensor, ids: torch.Tensor) -> torch.Tensor:
    """Shift: logits[:, :-1] predizem ids[:, 1:]."""
    return F.cross_entropy(logits[:, :-1, :].reshape(-1, logits.size(-1)), ids[:, 1:].reshape(-1))
