"""Tokenização BPE e custo PT vs EN em três 'tokenizers'."""

from __future__ import annotations

from typing import Any

from transformers import AutoTokenizer

PARES_PT_EN = [
    {
        "id": "sinistro",
        "pt": "O segurado Ana Souza abriu um sinistro na Amplitude Seguros.",
        "en": "The insured Ana Souza opened a claim at Amplitude Seguros.",
    },
    {
        "id": "placa",
        "pt": "A placa do veiculo e ABC-1D23.",
        "en": "The vehicle plate is ABC-1D23.",
    },
    {
        "id": "soma",
        "pt": "Quanto e doze mais sete? Responda apenas o numero.",
        "en": "What is twelve plus seven? Answer with the number only.",
    },
]

TOKENIZERS = {
    "smollm2": "HuggingFaceTB/SmolLM2-135M",
    "qwen25": "Qwen/Qwen2.5-0.5B",
    "caracteres": "caracteres",
}

FRASE_BPE = "Segurado"


class TokenizerCaracteres:
    """Baseline pedagógico: 1 caractere = 1 token. Sem download."""

    name = "caracteres"

    def encode(self, texto: str) -> list[int]:
        return [ord(c) % 256 for c in texto]

    def tokens(self, texto: str) -> list[str]:
        return list(texto)


def _hf(id_modelo: str):
    tok = AutoTokenizer.from_pretrained(id_modelo)
    return tok


def pecas(tok, texto: str) -> list[str]:
    ids = tok(texto, add_special_tokens=False).input_ids
    return tok.convert_ids_to_tokens(ids)


def medir(tok, texto: str, *, nome: str) -> dict[str, Any]:
    n_chars = len(texto)
    if nome == "caracteres":
        toks = tok.tokens(texto)
        ids = tok.encode(texto)
    else:
        ids = tok(texto, add_special_tokens=False).input_ids
        toks = tok.convert_ids_to_tokens(ids)
    n = len(ids)
    return {
        "n_tokens": n,
        "n_chars": n_chars,
        "tokens_por_char": (n / n_chars) if n_chars else None,
        "chars_por_token": (n_chars / n) if n else None,
        "tokens": toks,
        "ids": list(ids),
    }


def tabela_pt_en() -> dict[str, Any]:
    smol = _hf(TOKENIZERS["smollm2"])
    qwen = _hf(TOKENIZERS["qwen25"])
    char = TokenizerCaracteres()
    nomes = [("smollm2", smol), ("qwen25", qwen), ("caracteres", char)]
    linhas = []
    for par in PARES_PT_EN:
        linha: dict[str, Any] = {"id": par["id"], "pt": par["pt"], "en": par["en"]}
        for nome, tok in nomes:
            m_pt = medir(tok, par["pt"], nome=nome)
            m_en = medir(tok, par["en"], nome=nome)
            razao = (
                m_pt["n_tokens"] / m_en["n_tokens"] if m_en["n_tokens"] else None
            )
            rec = {
                "pt": {k: m_pt[k] for k in ("n_tokens", "n_chars", "tokens_por_char", "chars_por_token")},
                "en": {k: m_en[k] for k in ("n_tokens", "n_chars", "tokens_por_char", "chars_por_token")},
                "razao_pt_en": razao,
            }
            # listas de tokens só nos BPE (caracteres seria 1:1 com o texto)
            if nome != "caracteres":
                rec["tokens_pt"] = m_pt["tokens"]
                rec["tokens_en"] = m_en["tokens"]
            linha[nome] = rec
        linhas.append(linha)
    bpe = {
        "palavra": FRASE_BPE,
        "smollm2": pecas(smol, FRASE_BPE),
        "qwen25": pecas(qwen, FRASE_BPE),
        "caracteres": char.tokens(FRASE_BPE),
        "nota": "BPE parte palavra frequente em subpalavras; caracteres nunca junta.",
    }
    vocab = {
        "smollm2": int(getattr(smol, "vocab_size", len(smol))),
        "qwen25": int(getattr(qwen, "vocab_size", len(qwen))),
        "caracteres": 256,
    }
    return {
        "tokenizers": {
            "smollm2": TOKENIZERS["smollm2"],
            "qwen25": TOKENIZERS["qwen25"],
            "caracteres": "1 caractere = 1 token (baseline, sem card HF)",
        },
        "vocab_size": vocab,
        "pares": linhas,
        "quebra_bpe": bpe,
    }
