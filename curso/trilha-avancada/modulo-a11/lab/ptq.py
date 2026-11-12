"""PTQ weight-only INT8/INT4 sobre SmolLM2 — âncora enquanto A5/A6 não existem.

INT8 dinâmico: ``torch.ao.quantization.quantize_dynamic`` (CPU, Linear).
INT4 por grupo: fake-quant (desquantiza na conta) — mede *qualidade* dos 4 bits,
não velocidade. Calibração = corpus curto original (``frases.corpus_ppl``) para
perplexidade; as escalas INT4 vêm dos próprios pesos (weight-only).

Não republica wikitext. Não usa bitsandbytes (CUDA). GGUF/llama.cpp: leitura.
"""

from __future__ import annotations

import copy
import time
from typing import Any

import torch
from torch import nn

from frases import corpus_ppl

MODELO_PTQ = "HuggingFaceTB/SmolLM2-135M"


def _nbytes_tensor(t: torch.Tensor) -> int:
    if t.is_quantized:
        ir = t.int_repr()
        n = ir.numel() * ir.element_size()
        try:
            scale = t.q_scale()
            n += 4 if not torch.is_tensor(scale) else scale.numel() * 4
        except RuntimeError:
            n += 4
        return n
    return t.numel() * t.element_size()


def nbytes_estado(model: nn.Module) -> int:
    """Inclui pesos empacotados de ``quantize_dynamic`` (não aparecem em ``parameters()``)."""
    n = 0
    visto: set[int] = set()

    def add(t: torch.Tensor | None) -> None:
        nonlocal n
        if t is None or not torch.is_tensor(t) or id(t) in visto:
            return
        visto.add(id(t))
        n += _nbytes_tensor(t)

    for p in model.parameters():
        add(p)
    for b in model.buffers():
        add(b)
    for mod in model.modules():
        w = getattr(mod, "weight", None)
        if callable(w):
            try:
                add(w())
            except Exception:
                pass
        bias = getattr(mod, "bias", None)
        if callable(bias):
            try:
                add(bias())
            except Exception:
                pass
    return n


def quantizar_int4_por_grupo(peso: torch.Tensor, grupo: int = 64) -> tuple[torch.Tensor, torch.Tensor]:
    """Devolve (q em int8 no intervalo 0..15, scales por grupo) para a última dim."""
    original = peso.shape
    d = original[-1]
    pad = (grupo - d % grupo) % grupo
    w = peso.float().reshape(-1, d)
    if pad:
        w = torch.nn.functional.pad(w, (0, pad))
    g = w.shape[-1] // grupo
    w = w.view(-1, g, grupo)
    scale = w.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8) / 7.5  # 4 bits simétricos ≈ [-7.5, 7.5] níveis
    q = (w / scale).round().clamp(-8, 7)
    return q.to(torch.int8), scale.squeeze(-1)


def dequantizar_int4(q: torch.Tensor, scale: torch.Tensor, shape: torch.Size, grupo: int = 64) -> torch.Tensor:
    d = shape[-1]
    pad = (grupo - d % grupo) % grupo
    g = (d + pad) // grupo
    w = q.float() * scale.unsqueeze(-1)
    w = w.reshape(-1, g * grupo)
    if pad:
        w = w[:, :d]
    return w.reshape(shape)


def aplicar_fake_int4_lineares(model: nn.Module, grupo: int = 64) -> dict[str, Any]:
    """Substitui .weight de nn.Linear (exceto lm_head) por versão 4 bits desquantizada."""
    n_matrizes = 0
    packed = 0
    with torch.no_grad():
        for nome, mod in model.named_modules():
            if not isinstance(mod, nn.Linear):
                continue
            if nome.endswith("lm_head") or "embed" in nome:
                continue
            q, scale = quantizar_int4_por_grupo(mod.weight.data, grupo)
            rec = dequantizar_int4(q, scale, mod.weight.data.shape, grupo)
            packed += q.numel() // 2 + scale.numel() * 2  # 4 bits empacotados + scales fp16
            mod.weight.data.copy_(rec.to(mod.weight.dtype))
            n_matrizes += 1
    return {"matrizes": n_matrizes, "bytes_empacotados_estimados": packed, "grupo": grupo}


@torch.no_grad()
def perplexidade(model, tok, textos: list[str], device: str) -> float:
    nll = 0.0
    ntok = 0
    model.eval()
    for t in textos:
        ids = tok(t, return_tensors="pt")
        input_ids = ids.input_ids.to(device)
        if input_ids.size(1) < 2:
            continue
        out = model(input_ids, labels=input_ids)
        # HF CE já média por token não-mascarado
        n = input_ids.numel() - 1
        nll += float(out.loss) * n
        ntok += n
    return math_exp(nll / max(ntok, 1))


def math_exp(x: float) -> float:
    import math

    try:
        return math.exp(x)
    except OverflowError:
        return float("inf")


@torch.no_grad()
def latencia_generate(model, tok, texto: str, *, n_novos: int, use_cache: bool, device: str, corridas: int = 2) -> dict[str, float]:
    ids = tok(texto, return_tensors="pt").input_ids.to(device)
    tempos = []
    for _ in range(corridas):
        t0 = time.perf_counter()
        model.generate(
            ids,
            max_new_tokens=n_novos,
            min_new_tokens=n_novos,
            do_sample=False,
            use_cache=use_cache,
        )
        tempos.append(time.perf_counter() - t0)
    tempos.sort()
    med = tempos[len(tempos) // 2]
    return {
        "segundos_mediana": med,
        "tokens_por_s": n_novos / med if med else 0.0,
        "corridas": corridas,
        "n_novos": n_novos,
        "use_cache": use_cache,
        "prefixo": ids.size(1),
    }


def carregar_smol(device: str | None = None):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(MODELO_PTQ)
    model = AutoModelForCausalLM.from_pretrained(MODELO_PTQ, dtype=torch.float32)
    model.eval()
    model.to(device)
    return tok, model, device


def comparar_ptq(*, n_novos: int = 8, device: str | None = None) -> dict[str, Any]:
    tok, model, device = carregar_smol(device)
    textos = corpus_ppl()
    prompt = textos[0]

    t0 = time.perf_counter()
    ppl_fp32 = perplexidade(model, tok, textos, device)
    lat_fp32 = latencia_generate(model, tok, prompt, n_novos=n_novos, use_cache=True, device=device)
    bytes_fp32 = nbytes_estado(model)
    dt_fp32 = time.perf_counter() - t0

    t1 = time.perf_counter()
    modelo_int8 = torch.ao.quantization.quantize_dynamic(
        copy.deepcopy(model).cpu(), {nn.Linear}, dtype=torch.qint8
    )
    modelo_int8.eval()
    # generate/ppl no CPU após dynamic quant
    ppl_int8 = perplexidade(modelo_int8, tok, textos, "cpu")
    lat_int8 = latencia_generate(modelo_int8, tok, prompt, n_novos=n_novos, use_cache=True, device="cpu")
    bytes_int8 = nbytes_estado(modelo_int8)
    dt_int8 = time.perf_counter() - t1

    t2 = time.perf_counter()
    modelo_int4 = copy.deepcopy(model)
    meta_int4 = aplicar_fake_int4_lineares(modelo_int4)
    ppl_int4 = perplexidade(modelo_int4, tok, textos, device)
    lat_int4 = latencia_generate(modelo_int4, tok, prompt, n_novos=n_novos, use_cache=True, device=device)
    dt_int4 = time.perf_counter() - t2

    return {
        "modelo": MODELO_PTQ,
        "ancoragem": "SmolLM2-135M (A5/A6 ausentes; LoRA do M09 é a ponte conceitual, não os pesos)",
        "n_frases_ppl": len(textos),
        "fp32": {
            "ppl": ppl_fp32,
            "bytes": bytes_fp32,
            "latencia": lat_fp32,
            "segundos_bloco": round(dt_fp32, 3),
        },
        "int8_dinamico": {
            "ppl": ppl_int8,
            "bytes": bytes_int8,
            "latencia": lat_int8,
            "segundos_bloco": round(dt_int8, 3),
            "nota": "torch.ao.quantization.quantize_dynamic em Linear, CPU",
        },
        "int4_grupo64_fake": {
            "ppl": ppl_int4,
            "bytes_empacotados_estimados": meta_int4["bytes_empacotados_estimados"],
            "matrizes": meta_int4["matrizes"],
            "latencia": lat_int4,
            "segundos_bloco": round(dt_int4, 3),
            "nota": "fake-quant: compute em fp32; bytes são o empacotamento teórico",
        },
        "gguf_llama_cpp": "nao_calibrado",
        "bitsandbytes_llm_int8": "nao_calibrado_cpu",
        "nf4_qlora": "leitura_M09",
    }
