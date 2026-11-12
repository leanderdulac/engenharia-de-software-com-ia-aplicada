"""Log-prob da compleção dado o prompt — recompensa implícita sem reward model."""

from __future__ import annotations

from typing import Any

import torch
from torch import nn


def _ids(tok, texto: str) -> list[int]:
    return tok(texto, add_special_tokens=False).input_ids


@torch.no_grad()
def logprob_complecao(
    model: nn.Module,
    tok,
    prompt: str,
    complecao: str,
    *,
    device: str,
) -> tuple[float, int]:
    """Soma dos log P dos tokens da compleção. Devolve (soma, n_tokens)."""
    p_ids = _ids(tok, prompt)
    f_ids = _ids(tok, prompt + complecao)
    if len(f_ids) <= len(p_ids):
        # tokenizer comeu a compleção (raro em ASCII curto)
        return 0.0, 0
    ids = torch.tensor([f_ids], device=device)
    out = model(ids)
    logp = out.logits[:, :-1, :].log_softmax(dim=-1)
    alvo = ids[:, 1:]
    # tokens da compleção correspondem a posições len(p_ids)-1 .. len(f_ids)-2 no logit
    ini = max(len(p_ids) - 1, 0)
    lp = logp[0, ini:, :].gather(1, alvo[0, ini:].unsqueeze(-1)).squeeze(-1)
    return float(lp.sum()), int(lp.numel())


@torch.no_grad()
def avaliar_pares(
    model: nn.Module,
    tok,
    pares: list[dict[str, str]],
    *,
    device: str,
    modelo_ref: nn.Module | None = None,
) -> dict[str, Any]:
    model.eval()
    if modelo_ref is not None:
        modelo_ref.eval()
    rows = []
    for p in pares:
        lw, nw = logprob_complecao(model, tok, p["prompt"], p["chosen"], device=device)
        ll, nl = logprob_complecao(model, tok, p["prompt"], p["rejected"], device=device)
        if modelo_ref is None:
            rw, rl = lw, ll
        else:
            rw, _ = logprob_complecao(modelo_ref, tok, p["prompt"], p["chosen"], device=device)
            rl, _ = logprob_complecao(modelo_ref, tok, p["prompt"], p["rejected"], device=device)
        margin = (lw - ll) - (rw - rl)
        rows.append(
            {
                "logp_w": lw,
                "logp_l": ll,
                "logp_w_ref": rw,
                "logp_l_ref": rl,
                "n_w": nw,
                "n_l": nl,
                "margem_implicita": margin,
                "acerto": margin > 0,
                "acerto_bruto": lw > ll,
                "chosen_mais_curto": len(p["chosen"]) < len(p["rejected"]),
            }
        )
    n = max(len(rows), 1)
    acc = sum(r["acerto"] for r in rows) / len(rows) if rows else 0.0
    acc_b = sum(r["acerto_bruto"] for r in rows) / len(rows) if rows else 0.0
    margem = sum(r["margem_implicita"] for r in rows) / n
    return {
        "n": len(rows),
        "rewards_accuracies": acc,
        "preferencia_bruta": acc_b,
        "margem_media": margem,
        "fracao_chosen_mais_curto": sum(r["chosen_mais_curto"] for r in rows) / n,
        "linhas": rows,
    }


def tensores_do_relatorio(rel: dict[str, Any], device: str | torch.device = "cpu") -> dict[str, torch.Tensor]:
    linhas = rel["linhas"]
    def col(k: str) -> torch.Tensor:
        return torch.tensor([r[k] for r in linhas], dtype=torch.float32, device=device)

    return {
        "logp_w": col("logp_w"),
        "logp_l": col("logp_l"),
        "logp_w_ref": col("logp_w_ref"),
        "logp_l_ref": col("logp_l_ref"),
        "n_w": col("n_w"),
        "n_l": col("n_l"),
    }
