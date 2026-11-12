"""Template de chat declarado + labels −100 no prefixo.

SmolLM2-135M *base* não traz ``chat_template`` no tokenizer (o Instruct não
foi baixado). O template abaixo é desta trilha.
"""

from __future__ import annotations

from typing import Any

IGNORE = -100

# Marcadores ASCII para não depender de tokens especiais inexistentes no base.
TPL_SYS = "### system\n{sys}\n"
TPL_USER = "### user\n{user}\n"
TPL_ASST = "### assistant\n{asst}"


def renderizar(user: str, assistant: str, *, system: str | None) -> tuple[str, str]:
    """Devolve (prefixo incluindo cabeçalho do assistant, texto completo)."""
    prefixo = ""
    if system:
        prefixo += TPL_SYS.format(sys=system)
    prefixo += TPL_USER.format(user=user)
    prefixo += "### assistant\n"
    completo = prefixo + assistant
    return prefixo, completo


def tensorizar(tok, user: str, assistant: str, *, system: str | None, eos: bool = True) -> dict[str, Any]:
    """Concatena encodings do prefixo e do assistant (fronteira BPE explícita).

    Re-encodar a string inteira pode fundir tokens na junção e desalinharia
    ``n_prompt``. O SFTTrainer faz o mesmo recorte por template de resposta.
    """
    prefixo, _completo_str = renderizar(user, assistant, system=system)
    asst = assistant + (tok.eos_token or "") if eos else assistant
    ids_pref = tok(prefixo, add_special_tokens=False).input_ids
    ids_asst = tok(asst, add_special_tokens=False).input_ids
    ids_full = ids_pref + ids_asst
    n_p = len(ids_pref)
    labels = [IGNORE] * n_p + list(ids_asst)
    n_treino = len(ids_asst)
    eos_id = getattr(tok, "eos_token_id", None)
    return {
        "input_ids": ids_full,
        "labels": labels,
        "attention_mask": [1] * len(ids_full),
        "n_prompt": n_p,
        "n_total": len(ids_full),
        "n_assistant": n_treino,
        "fracao_prompt": n_p / max(len(ids_full), 1),
        "termina_eos": bool(eos and eos_id is not None and ids_full and ids_full[-1] == eos_id),
        "prefixo": prefixo,
        "completo": prefixo + asst,
    }


def lote(tok, dialogos: list[dict], *, system: str | None) -> list[dict[str, Any]]:
    return [
        tensorizar(tok, d["user"], d["assistant"], system=system) for d in dialogos
    ]


def tensorizar_turnos(
    tok,
    turnos: list[tuple[str, str]],
    *,
    system: str | None,
    eos: bool = True,
) -> dict[str, Any]:
    """Multi-turn: só segmentos ``assistant`` entram na loss (não o user)."""
    texto = ""
    if system:
        texto += TPL_SYS.format(sys=system)
    labels: list[int] = []
    ids: list[int] = []
    for papel, corpo in turnos:
        if papel == "user":
            trecho = TPL_USER.format(user=corpo)
            trecho_ids = tok(trecho, add_special_tokens=False).input_ids
            ids.extend(trecho_ids)
            labels.extend([IGNORE] * len(trecho_ids))
        elif papel == "assistant":
            cab = "### assistant\n"
            cab_ids = tok(cab, add_special_tokens=False).input_ids
            corpo_txt = corpo
            if eos and tok.eos_token:
                corpo_txt = corpo + tok.eos_token
            corpo_ids = tok(corpo_txt, add_special_tokens=False).input_ids
            ids.extend(cab_ids + corpo_ids)
            labels.extend([IGNORE] * len(cab_ids) + list(corpo_ids))
            texto += cab + corpo_txt
        else:
            raise ValueError(papel)
        if papel == "user":
            texto += trecho
    assert len(ids) == len(labels)
    n_asst = sum(1 for x in labels if x != IGNORE)
    return {
        "input_ids": ids,
        "labels": labels,
        "n_total": len(ids),
        "n_assistant": n_asst,
        "n_prompt": len(ids) - n_asst,
    }


def colar(
    itens: list[dict[str, Any]],
    pad_id: int,
    *,
    max_len: int | None = None,
) -> dict[str, Any]:
    """Padding à direita; labels de pad = −100; attention_mask 0 no pad.

    Truncamento à direita se ``max_len``: corta o fim (pode perder assistant).
    """
    comprimentos = [i["n_total"] for i in itens]
    L = max(comprimentos)
    truncou = False
    if max_len is not None and L > max_len:
        L = max_len
        truncou = True
    batch_ids: list[list[int]] = []
    batch_lab: list[list[int]] = []
    batch_msk: list[list[int]] = []
    n_asst_depois = []
    for i in itens:
        ids = list(i["input_ids"][:L])
        lab = list(i["labels"][:L])
        msk = [1] * len(ids)
        while len(ids) < L:
            ids.append(pad_id)
            lab.append(IGNORE)
            msk.append(0)
        batch_ids.append(ids)
        batch_lab.append(lab)
        batch_msk.append(msk)
        n_asst_depois.append(sum(1 for x in lab if x != IGNORE))
    return {
        "input_ids": batch_ids,
        "labels": batch_lab,
        "attention_mask": batch_msk,
        "L": L,
        "truncou": truncou,
        "n_assistant_medio_depois": sum(n_asst_depois) / len(n_asst_depois),
        "n_assistant_medio_antes": sum(i["n_assistant"] for i in itens) / len(itens),
    }


def resumo(itens: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(itens)
    return {
        "n": n,
        "n_prompt_medio": round(sum(i["n_prompt"] for i in itens) / n, 2),
        "n_total_medio": round(sum(i["n_total"] for i in itens) / n, 2),
        "n_assistant_medio": round(sum(i["n_assistant"] for i in itens) / n, 2),
        "fracao_prompt_media": round(sum(i.get("fracao_prompt", i["n_prompt"] / i["n_total"]) for i in itens) / n, 4),
        "todos_eos": all(i.get("termina_eos", True) for i in itens),
        "labels_prompt_menos_100": all(
            all(x == IGNORE for x in i["labels"][: i["n_prompt"]]) for i in itens
        ),
    }
