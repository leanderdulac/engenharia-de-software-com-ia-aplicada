"""Lab A2.2: abrir um LLM pequeno, contar parâmetros e reconstruir um bloco.

Padrão (CPU / Colab gratuito): ``HuggingFaceTB/SmolLM2-135M`` (Apache-2.0).
Opcional: ``TRILHA_A2_MODELO=Qwen/Qwen2.5-0.5B`` (também Apache-2.0; mais pesado).

A reconstrução usa os *pesos* do bloco (projeções, normas, MLP) e a matemática
deste laboratório (RMSNorm, RoPE, GQA, softmax causal, SwiGLU). Não chama
``layer.forward``.
"""

from __future__ import annotations

import os
from typing import Any

import torch
import torch.nn.functional as F

from atencao import atencao_produto_interno_escalado, juntar_cabecas, repetir_kv
from normas import rms_norm
from posicional import aplicar_rope

MODELO_PADRAO = "HuggingFaceTB/SmolLM2-135M"
FRASE_PADRAO = "Segurado: Ana Souza. Placa: ABC-1D23."


def id_do_modelo() -> str:
    return os.environ.get("TRILHA_A2_MODELO", MODELO_PADRAO)


def carregar(modelo_id: str | None = None, device: str | None = None):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    modelo_id = modelo_id or id_do_modelo()
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(modelo_id)
    kwargs: dict[str, Any] = {
        "attn_implementation": "eager",
        "dtype": torch.float32,
    }
    model = AutoModelForCausalLM.from_pretrained(modelo_id, **kwargs)
    model.eval()
    model.to(device)
    return tok, model, device


def ler_config(model) -> dict[str, Any]:
    c = model.config
    rope = getattr(c, "rope_parameters", None) or getattr(c, "rope_scaling", None) or {}
    if not isinstance(rope, dict):
        rope = {}
    n_q = int(c.num_attention_heads)
    n_kv = int(getattr(c, "num_key_value_heads", n_q))
    return {
        "model_type": c.model_type,
        "arquiteturas": list(getattr(c, "architectures", []) or []),
        "hidden_size": int(c.hidden_size),
        "intermediate_size": int(c.intermediate_size),
        "num_hidden_layers": int(c.num_hidden_layers),
        "num_attention_heads": n_q,
        "num_key_value_heads": n_kv,
        "gqa": n_kv != n_q,
        "n_rep_kv": n_q // n_kv,
        "head_dim": int(getattr(c, "head_dim", c.hidden_size // n_q)),
        "hidden_act": getattr(c, "hidden_act", None),
        "rms_norm_eps": float(c.rms_norm_eps),
        "rope_theta": rope.get("rope_theta", getattr(c, "default_theta", None)),
        "rope_type": rope.get("rope_type", "default"),
        "vocab_size": int(c.vocab_size),
        "max_position_embeddings": int(c.max_position_embeddings),
        "tie_word_embeddings": bool(getattr(c, "tie_word_embeddings", False)),
        "attention_bias": bool(getattr(c, "attention_bias", False)),
    }


def _balde(nome: str) -> str:
    n = nome.lower()
    if "embed_tokens" in n or n.endswith(".embed_tokens.weight") or "wte" in n:
        return "embedding"
    if "lm_head" in n:
        return "lm_head"
    if any(p in n for p in ("q_proj", "k_proj", "v_proj", "o_proj", "self_attn", "query", "key", "value")):
        return "atencao"
    if any(p in n for p in ("mlp", "gate_proj", "up_proj", "down_proj", "fc1", "fc2")):
        return "ffn"
    if "norm" in n:
        return "norm"
    return "outros"


def contar_parametros(model) -> dict[str, Any]:
    visto: set[int] = set()
    por = {k: 0 for k in ("embedding", "atencao", "ffn", "norm", "lm_head", "outros")}
    for nome, p in model.named_parameters():
        if id(p) in visto:
            continue
        visto.add(id(p))
        por[_balde(nome)] += int(p.numel())
    total_nosso = sum(por.values())
    total_hf = int(model.num_parameters())
    return {
        "por_componente": por,
        "total_unico": total_nosso,
        "num_parameters": total_hf,
        "erro_relativo": abs(total_nosso - total_hf) / max(total_hf, 1),
    }


def _rotary(model):
    if hasattr(model, "model") and hasattr(model.model, "rotary_emb"):
        return model.model.rotary_emb
    layer0 = model.model.layers[0]
    if hasattr(layer0, "self_attn") and hasattr(layer0.self_attn, "rotary_emb"):
        return layer0.self_attn.rotary_emb
    raise AttributeError("não achei rotary_emb neste modelo")


def _camadas(model):
    return model.model.layers


def reconstruir_bloco(
    model,
    x: torch.Tensor,
    position_ids: torch.Tensor,
    *,
    camada: int = 0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Aplica o bloco ``camada`` com a nossa matemática. ``x`` é o hidden de entrada."""
    cfg = ler_config(model)
    layer = _camadas(model)[camada]
    b, s, _ = x.shape
    n_q, n_kv, d_h = cfg["num_attention_heads"], cfg["num_key_value_heads"], cfg["head_dim"]
    eps = cfg["rms_norm_eps"]
    n_rep = cfg["n_rep_kv"]

    residual = x
    h = rms_norm(x, layer.input_layernorm.weight, eps)
    q = layer.self_attn.q_proj(h)
    k = layer.self_attn.k_proj(h)
    v = layer.self_attn.v_proj(h)
    q = q.view(b, s, n_q, d_h).transpose(1, 2).contiguous()
    k = k.view(b, s, n_kv, d_h).transpose(1, 2).contiguous()
    v = v.view(b, s, n_kv, d_h).transpose(1, 2).contiguous()
    cos, sin = _rotary(model)(x, position_ids)
    q, k = aplicar_rope(q, k, cos, sin)
    k = repetir_kv(k, n_rep)
    v = repetir_kv(v, n_rep)
    ctx, pesos = atencao_produto_interno_escalado(q, k, v, causal=True)
    attn = layer.self_attn.o_proj(juntar_cabecas(ctx))
    x = residual + attn
    residual = x
    h = rms_norm(x, layer.post_attention_layernorm.weight, eps)
    # SwiGLU: silu(gate) * up, depois down — Qwen2 / Llama / SmolLM2
    mlp = layer.mlp
    h = mlp.down_proj(F.silu(mlp.gate_proj(h)) * mlp.up_proj(h))
    return residual + h, pesos


@torch.no_grad()
def inspecionar(
    *,
    modelo_id: str | None = None,
    frase: str = FRASE_PADRAO,
    camada: int = 0,
    cabeca: int = 0,
    device: str | None = None,
) -> dict[str, Any]:
    tok, model, device = carregar(modelo_id, device)
    modelo_id = modelo_id or id_do_modelo()
    cfg = ler_config(model)
    contagem = contar_parametros(model)
    ids = tok(frase, return_tensors="pt")
    input_ids = ids.input_ids.to(device)
    b, s = input_ids.shape
    position_ids = torch.arange(s, device=device).unsqueeze(0).expand(b, -1)
    tokens = tok.convert_ids_to_tokens(input_ids[0])

    saida = model(
        input_ids=input_ids,
        position_ids=position_ids,
        output_hidden_states=True,
        output_attentions=True,
        use_cache=False,
    )
    x_in = saida.hidden_states[camada]
    x_ref = saida.hidden_states[camada + 1]
    x_nossa, pesos = reconstruir_bloco(model, x_in, position_ids, camada=camada)
    delta = (x_nossa - x_ref).abs()
    mapa_hf = saida.attentions[camada][0, cabeca].cpu()
    mapa_nossa = pesos[0, cabeca].cpu()

    return {
        "modelo": modelo_id,
        "licenca_card": "Apache-2.0 (conferir o card se trocar o id)",
        "frase": frase,
        "tokens": tokens,
        "n_tokens": len(tokens),
        "config": cfg,
        "parametros": contagem,
        "bloco_reconstruido": {
            "camada": camada,
            "diff_max": float(delta.max()),
            "diff_media": float(delta.mean()),
            "diff_atencao_max": float((mapa_nossa - mapa_hf).abs().max()),
        },
        "atencao": {
            "camada": camada,
            "cabeca": cabeca,
            "mapa": mapa_hf.tolist(),
            "causal_ok": bool((mapa_hf.triu(1) < 1e-6).all()),
        },
        "num_parameters": contagem["num_parameters"],
    }


def mapa_ascii(tokens: list[str], mapa: list[list[float]], *, casas: int = 2) -> str:
    """Heatmap tosco para colar no relatório (linhas = consulta, colunas = chave)."""
    rotulos = [t.replace("Ġ", " ").replace("▁", " ")[:6] for t in tokens]
    cab = "      " + " ".join(f"{r:>6}" for r in rotulos)
    linhas = [cab]
    for i, linha in enumerate(mapa):
        nums = " ".join(f"{v:>6.{casas}f}" for v in linha)
        linhas.append(f"{rotulos[i]:>6} {nums}")
    return "\n".join(linhas)
