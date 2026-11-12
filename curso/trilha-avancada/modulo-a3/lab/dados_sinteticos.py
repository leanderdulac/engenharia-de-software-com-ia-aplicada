"""Corpus sintético — *não* é o dump TinyStories.

Cada token é (anterior + 1) mod vocab. O modelo deve aprender a contar.
"""

from __future__ import annotations

import torch


def lote_contador(n: int, seq: int, vocab: int, *, semente: int, device: str = "cpu") -> torch.Tensor:
    g = torch.Generator().manual_seed(semente)
    inicio = torch.randint(0, vocab, (n, 1), generator=g)
    ids = inicio.repeat(1, seq).clone()
    for t in range(1, seq):
        ids[:, t] = (ids[:, t - 1] + 1) % vocab
    return ids.to(device)
