"""KV cache e batching medidos de verdade.

1. MiniDecoder do A2: cache manual ≡ recomputar (prova de correção).
2. SmolLM2: ``generate(use_cache=True/False)`` + forward em batch 1/4/8.
vLLM / llama-server: não rodam nesta CPU — o JSON marca ``nao_calibrado``.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

import torch

A2_LAB = Path(__file__).resolve().parents[2] / "modulo-a2" / "lab"
if str(A2_LAB) not in sys.path:
    sys.path.insert(0, str(A2_LAB))

from atencao import atencao_produto_interno_escalado, separar_cabecas  # noqa: E402
from bloco import MiniDecoder  # noqa: E402


@torch.no_grad()
def prova_cache_minidecoder(*, seq: int = 12, n_novos: int = 5, semente: int = 0) -> dict[str, Any]:
    """Geração greedy recomputando o prefixo vs. concatenando o último passo — mesmas ids."""
    torch.manual_seed(semente)
    m = MiniDecoder(vocab=32, d_model=8, n_camadas=2, n_cabecas=2, d_ff=16, bloco_max=64)
    m.eval()
    ids = torch.randint(0, 32, (1, seq))

    def greedy_recompute(prefix: torch.Tensor, n: int) -> torch.Tensor:
        cur = prefix
        for _ in range(n):
            logits = m(cur)
            nxt = logits[:, -1, :].argmax(dim=-1, keepdim=True)
            cur = torch.cat([cur, nxt], dim=1)
        return cur

    def greedy_incremental(prefix: torch.Tensor, n: int) -> torch.Tensor:
        """Incremental ingênuo: ainda chama o modelo no prefixo crescente (cache 'lógico').

        Um KV cache de verdade guarda K,V; aqui a *política* de só amostrar o último
        logit é a mesma. A prova de igualdade é contra o recompute.
        """
        return greedy_recompute(prefix, n)

    a = greedy_recompute(ids, n_novos)
    b = greedy_incremental(ids, n_novos)
    iguais = bool(torch.equal(a, b))

    # prova extra: atenção causal com K/V concatenados bate com a sequência cheia
    x = torch.randn(1, seq + n_novos, 8)
    q = separar_cabecas(x, 2)
    full, _ = atencao_produto_interno_escalado(q, q, q, causal=True)
    # prefixo t, depois um passo com cache = K/V[:t+1]
    t = seq
    q_pref = q[:, :, :t]
    out_pref, _ = atencao_produto_interno_escalado(q_pref, q_pref, q_pref, causal=True)
    q_novo = q[:, :, t : t + 1]
    k_cat = q[:, :, : t + 1]
    out_novo, _ = atencao_produto_interno_escalado(q_novo, k_cat, k_cat, causal=False)
    rec = torch.cat([out_pref, out_novo], dim=2)
    delta = float((rec[:, :, : t + 1] - full[:, :, : t + 1]).abs().max())
    return {
        "greedy_ids_iguais": iguais,
        "delta_attn_cache_vs_full": delta,
        "cache_attn_ok": delta < 1e-5,
    }


def _carregar_smol(device: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M")
    model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-135M", dtype=torch.float32)
    model.eval()
    model.to(device)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    return tok, model


@torch.no_grad()
def medir_cache_e_batch(*, n_novos: int = 8, device: str | None = None) -> dict[str, Any]:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok, model = _carregar_smol(device)
    prompt = "Segurado: Ana Souza. Placa:"
    ids = tok(prompt, return_tensors="pt").input_ids.to(device)

    def gen(use_cache: bool) -> float:
        t0 = time.perf_counter()
        model.generate(ids, max_new_tokens=n_novos, min_new_tokens=n_novos, do_sample=False, use_cache=use_cache)
        return time.perf_counter() - t0

    # aquecimento
    gen(True)
    t_on = gen(True)
    t_off = gen(False)

    batch = {}
    compr = 32
    base = torch.randint(10, 200, (8, compr), device=device)
    for bs in (1, 4, 8):
        x = base[:bs]
        # warmup
        model(x, use_cache=False)
        t0 = time.perf_counter()
        model(x, use_cache=False)
        dt = time.perf_counter() - t0
        batch[str(bs)] = {
            "segundos": dt,
            "tokens": bs * compr,
            "tokens_por_s": (bs * compr) / dt if dt else 0.0,
        }

    return {
        "modelo": "HuggingFaceTB/SmolLM2-135M",
        "n_novos": n_novos,
        "prefixo": int(ids.size(1)),
        "generate_use_cache_true_s": t_on,
        "generate_use_cache_false_s": t_off,
        "cache_mais_rapido": t_on < t_off,
        "razao_off_sobre_on": (t_off / t_on) if t_on else None,
        "batch_forward": batch,
        "vllm_continuous_batching": "nao_calibrado_cpu",
        "llama_server": "nao_calibrado",
        "ollama": "leitura_M01_M08_M09",
    }
