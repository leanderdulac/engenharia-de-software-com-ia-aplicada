"""Um bloco decoder-only de brinquedo (pré-norma) + FFN estilo Vaswani ou SwiGLU."""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F

from atencao import atencao_produto_interno_escalado, juntar_cabecas, separar_cabecas
from normas import layer_norm
from posicional import embeddings_posicionais_sinusoidais


class FFNVaswani(nn.Module):
    """Position-wise FFN do paper: ReLU, ``d_ff`` em geral 4× ``d_model`` (§3.3)."""

    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.sobe = nn.Linear(d_model, d_ff)
        self.desce = nn.Linear(d_ff, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.desce(F.relu(self.sobe(x)))


class FFNSwiGLU(nn.Module):
    """Gated FFN dos LLMs atuais (Shazeer 2020): SiLU(xW_g) ⊙ (xW_u), depois W_d."""

    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.portao = nn.Linear(d_model, d_ff, bias=False)
        self.sobe = nn.Linear(d_model, d_ff, bias=False)
        self.desce = nn.Linear(d_ff, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.desce(F.silu(self.portao(x)) * self.sobe(x))


class BlocoDecoder(nn.Module):
    """Pré-norma, atenção causal multi-cabeça, resíduo, FFN, resíduo.

    O paper de 2017 usava *pós*-norma (LayerNorm depois da soma). Os LLMs que o
    A2 abre usam *pré*-norma. Este bloco segue o desenho moderno de propósito:
    é o que você vai reconstruir no Lab A2.2.
    """

    def __init__(
        self,
        d_model: int = 8,
        n_cabecas: int = 2,
        d_ff: int = 16,
        *,
        swiglu: bool = False,
        eps: float = 1e-5,
    ):
        super().__init__()
        if d_model % n_cabecas != 0:
            raise ValueError("d_model precisa ser múltiplo de n_cabecas")
        self.d_model = d_model
        self.n_cabecas = n_cabecas
        self.q = nn.Linear(d_model, d_model, bias=False)
        self.k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Linear(d_model, d_model, bias=False)
        self.o = nn.Linear(d_model, d_model, bias=False)
        self.ln1_peso = nn.Parameter(torch.ones(d_model))
        self.ln1_vies = nn.Parameter(torch.zeros(d_model))
        self.ln2_peso = nn.Parameter(torch.ones(d_model))
        self.ln2_vies = nn.Parameter(torch.zeros(d_model))
        self.eps = eps
        self.ffn = FFNSwiGLU(d_model, d_ff) if swiglu else FFNVaswani(d_model, d_ff)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        residual = x
        h = layer_norm(x, self.ln1_peso, self.ln1_vies, self.eps)
        q = separar_cabecas(self.q(h), self.n_cabecas)
        k = separar_cabecas(self.k(h), self.n_cabecas)
        v = separar_cabecas(self.v(h), self.n_cabecas)
        ctx, pesos = atencao_produto_interno_escalado(q, k, v, causal=True)
        x = residual + self.o(juntar_cabecas(ctx))
        residual = x
        h = layer_norm(x, self.ln2_peso, self.ln2_vies, self.eps)
        x = residual + self.ffn(h)
        return x, pesos


class MiniDecoder(nn.Module):
    """Tokens → embedding + senoide → N blocos → norma → logits (weight tying)."""

    def __init__(
        self,
        vocab: int = 32,
        d_model: int = 8,
        n_camadas: int = 2,
        n_cabecas: int = 2,
        d_ff: int = 16,
        bloco_max: int = 32,
    ):
        super().__init__()
        self.emb = nn.Embedding(vocab, d_model)
        self.blocos = nn.ModuleList(
            BlocoDecoder(d_model, n_cabecas, d_ff) for _ in range(n_camadas)
        )
        self.ln_f_peso = nn.Parameter(torch.ones(d_model))
        self.ln_f_vies = nn.Parameter(torch.zeros(d_model))
        pe = embeddings_posicionais_sinusoidais(bloco_max, d_model)
        self.register_buffer("pe", pe, persistent=False)

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        s = ids.size(1)
        x = self.emb(ids) + self.pe[:s]
        for bloco in self.blocos:
            x, _ = bloco(x)
        x = layer_norm(x, self.ln_f_peso, self.ln_f_vies)
        return F.linear(x, self.emb.weight)  # amarra embedding e cabeça
