"""Latência p50/p95, tokens/s e pico de RSS — números do processo."""

from __future__ import annotations

import statistics
import time
from typing import Any

import torch

from versoes import rss_mb

PROMPTS = [
    "Responda apenas o numero inteiro.\n1+1=",
    "Responda apenas o numero inteiro.\n2+2=",
    "Responda apenas o numero inteiro.\n3+4=",
    "Segurado: Ana Souza. Placa: ABC-1D23. Extraia a placa:",
    "Complete: A placa do veiculo e",
]


def _percentil(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    k = min(len(ys) - 1, max(0, int(round((p / 100) * (len(ys) - 1)))))
    return ys[k]


@torch.no_grad()
def gerar_lote(
    model,
    tok,
    prompts: list[str],
    *,
    max_novos: int = 8,
    semente: int = 0,
    device: str = "cpu",
) -> dict[str, Any]:
    torch.manual_seed(semente)
    model.eval()
    lado = getattr(tok, "padding_side", "right")
    tok.padding_side = "left"
    lat: list[float] = []
    n_tok = 0
    rss_pico = rss_mb() or 0.0
    t_wall = time.perf_counter()
    try:
        for p in prompts:
            enc = tok(p, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items()}
            in_len = enc["input_ids"].shape[1]
            t0 = time.perf_counter()
            out = model.generate(
                **enc,
                max_new_tokens=max_novos,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
            lat.append(time.perf_counter() - t0)
            n_tok += int(out.shape[1] - in_len)
            r = rss_mb()
            if r is not None:
                rss_pico = max(rss_pico, r)
    finally:
        tok.padding_side = lado
    wall = time.perf_counter() - t_wall
    pegada = None
    fn = getattr(model, "get_memory_footprint", None)
    if fn is not None:
        pegada = round(fn() / 1e6, 1)
    return {
        "n": len(prompts),
        "semente": semente,
        "max_novos": max_novos,
        "latencia_p50_s": _percentil(lat, 50),
        "latencia_p95_s": _percentil(lat, 95),
        "latencia_media_s": statistics.fmean(lat) if lat else None,
        "tokens_gerados": n_tok,
        "tokens_por_s": (n_tok / wall) if wall else None,
        "wall_s": round(wall, 3),
        "rss_pico_mb": rss_pico,
        "pegada_mb": pegada,
        "latencias_s": [round(x, 4) for x in lat],
    }


def p50_dentro_de(a: float, b: float, *, tol: float = 0.20) -> bool:
    if a <= 0 or b <= 0:
        return False
    return abs(a - b) / min(a, b) <= tol
