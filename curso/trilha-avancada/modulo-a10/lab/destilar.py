"""Destilação por resposta (CE), por logits (KL + T²) e perda mista Hinton."""

from __future__ import annotations

from typing import Any, Literal

import torch
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from licencas import ALUNO

ModoMascara = Literal["resposta", "prompt", "primeiro", "tudo"]


def _tok(modelo: str):
    tok = AutoTokenizer.from_pretrained(modelo)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok


def _peft(model):
    cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )
    return get_peft_model(model, cfg)


def _ids(tok, prompt: str, complecao: str) -> tuple[list[int], int]:
    p = tok(prompt, add_special_tokens=False).input_ids
    f = tok(prompt + complecao, add_special_tokens=False).input_ids
    return f, len(p)


def mascara_shift(n_prompt: int, n_seq: int, modo: ModoMascara = "resposta") -> torch.Tensor:
    """Booleana sobre ``logits[:, :-1]`` (posição ``j`` prediz ``ids[j+1]``).

    Tokens da resposta ocupam ``ids[n_prompt:]``. A primeira predição da
    resposta é ``j = n_prompt - 1``. Isso é o *shift* causal: não se alinha
    ``logits[t]`` com ``ids[t]``, e sim com ``ids[t+1]``.
    """
    n_pred = max(n_seq - 1, 0)
    m = torch.zeros(n_pred, dtype=torch.bool)
    if n_pred == 0:
        return m
    ini_resposta = max(n_prompt - 1, 0)
    if modo == "tudo":
        m[:] = True
    elif modo == "resposta":
        m[ini_resposta:] = True
    elif modo == "primeiro":
        if ini_resposta < n_pred:
            m[ini_resposta] = True
    elif modo == "prompt":
        m[:ini_resposta] = True
    else:
        raise ValueError(f"modo desconhecido: {modo}")
    return m


def carregar_aluno(device: str = "cpu"):
    """Aluno = π_SFT mergeado + LoRA novo, ou base + LoRA se A5 desligado."""
    import sys
    from pathlib import Path

    a5 = Path(__file__).resolve().parents[2] / "modulo-a5" / "lab"
    if str(a5) not in sys.path:
        sys.path.insert(0, str(a5))
    from pi_sft import carregar_base_ou_sft, resolver

    if resolver() is not None:
        m, tok, _info = carregar_base_ou_sft(device=device)
        m = _peft(m)
        m.to(device)
        return m, tok
    tok = _tok(ALUNO)
    m = AutoModelForCausalLM.from_pretrained(ALUNO, dtype=torch.float32)
    m = _peft(m)
    m.to(device)
    return m, tok


def _forward_shift(model, ids: torch.Tensor) -> torch.Tensor:
    return model(ids).logits[:, :-1, :]


def _ce_mascarada(logp: torch.Tensor, alvo: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """``logp`` e ``alvo`` em ``[1, S-1, ...]`` / ``[1, S-1]``; ``mask`` em ``[S-1]``."""
    n = mask.sum().clamp(min=1)
    lp = logp.gather(-1, alvo.unsqueeze(-1)).squeeze(-1)
    return -(lp * mask).sum() / n


def _kl_mascarada(
    logits_s: torch.Tensor,
    logits_t: torch.Tensor,
    mask: torch.Tensor,
    temperatura: float,
    *,
    aplicar_t2: bool = True,
) -> torch.Tensor:
    """KL(p_T || p_S) média nas posições da máscara; opcionalmente × T² (Hinton §2)."""
    t = temperatura
    log_s = F.log_softmax(logits_s / t, dim=-1)
    p_t = F.softmax(logits_t / t, dim=-1)
    kl_tok = F.kl_div(log_s, p_t, reduction="none").sum(dim=-1)
    n = mask.sum().clamp(min=1)
    kl = (kl_tok * mask).sum() / n
    if aplicar_t2:
        kl = kl * (t ** 2)
    return kl


def loss_sequencia(model, tok, prompt: str, complecao: str, device: str) -> torch.Tensor:
    f_ids, n_p = _ids(tok, prompt, complecao)
    if len(f_ids) <= n_p:
        return torch.zeros((), device=device, requires_grad=True)
    ids = torch.tensor([f_ids], device=device)
    mask = mascara_shift(n_p, ids.size(1), "resposta").to(device)
    logp = _forward_shift(model, ids).log_softmax(dim=-1)
    alvo = ids[:, 1:]
    return _ce_mascarada(logp, alvo, mask)


def loss_logits(
    student,
    teacher,
    tok,
    prompt: str,
    complecao: str,
    *,
    temperatura: float,
    device: str,
    modo_mascara: ModoMascara = "resposta",
    aplicar_t2: bool = True,
) -> torch.Tensor:
    f_ids, n_p = _ids(tok, prompt, complecao)
    if len(f_ids) <= n_p:
        return torch.zeros((), device=device, requires_grad=True)
    ids = torch.tensor([f_ids], device=device)
    mask = mascara_shift(n_p, ids.size(1), modo_mascara).to(device)
    s = _forward_shift(student, ids)
    with torch.no_grad():
        t = _forward_shift(teacher, ids)
    return _kl_mascarada(s, t, mask, temperatura, aplicar_t2=aplicar_t2)


def loss_mista(
    student,
    teacher,
    tok,
    prompt: str,
    complecao: str,
    *,
    temperatura: float,
    alpha: float,
    device: str,
    modo_mascara: ModoMascara = "resposta",
) -> torch.Tensor:
    """Hinton: ``α · CE(rótulos duros) + (1−α) · T² · KL(p_T || p_S)``.

    CE e KL usam a **mesma** máscara de resposta e o **mesmo** shift.
    """
    f_ids, n_p = _ids(tok, prompt, complecao)
    if len(f_ids) <= n_p:
        return torch.zeros((), device=device, requires_grad=True)
    ids = torch.tensor([f_ids], device=device)
    mask = mascara_shift(n_p, ids.size(1), modo_mascara).to(device)
    s = _forward_shift(student, ids)
    with torch.no_grad():
        t = _forward_shift(teacher, ids)
    ce = _ce_mascarada(s.log_softmax(dim=-1), ids[:, 1:], mask)
    kl = _kl_mascarada(s, t, mask, temperatura, aplicar_t2=True)
    return alpha * ce + (1.0 - alpha) * kl


def diagnosticar_kl(
    student,
    teacher,
    tok,
    prompt: str,
    complecao: str,
    *,
    temperatura: float = 2.0,
    device: str = "cpu",
) -> dict[str, Any]:
    """Confere máscara, shift e escala T² num único par (sem treinar)."""
    f_ids, n_p = _ids(tok, prompt, complecao)
    n_seq = len(f_ids)
    ids = torch.tensor([f_ids], device=device)
    with torch.no_grad():
        s = _forward_shift(student, ids)
        t = _forward_shift(teacher, ids)
    masks = {modo: mascara_shift(n_p, n_seq, modo).to(device) for modo in ("resposta", "prompt", "primeiro", "tudo")}
    kls: dict[str, float] = {}
    for modo, mask in masks.items():
        if mask.any():
            kls[modo] = float(_kl_mascarada(s, t, mask, temperatura, aplicar_t2=True).detach())
        else:
            kls[modo] = 0.0
    kl_sem_t2 = float(_kl_mascarada(s, t, masks["resposta"], temperatura, aplicar_t2=False).detach()) if masks["resposta"].any() else 0.0
    kl_com_t2 = kls["resposta"]
    razao = (kl_com_t2 / kl_sem_t2) if kl_sem_t2 else None
    n_resp = int(masks["resposta"].sum())
    n_prompt_pred = int(masks["prompt"].sum())
    ini = max(n_p - 1, 0)
    return {
        "n_prompt": n_p,
        "n_seq": n_seq,
        "n_complecao": n_seq - n_p,
        "n_posicoes_kl_resposta": n_resp,
        "n_posicoes_ce_resposta": n_resp,
        "n_posicoes_prompt": n_prompt_pred,
        "shift_alinhado": n_resp == max(n_seq - n_p, 0) and (ini + n_resp == n_seq - 1 or n_resp == 0),
        "mascara_inclui_prompt": bool(n_prompt_pred > 0 and (masks["resposta"] & masks["prompt"]).any()),
        "primeira_posicao_resposta": ini,
        "kl_resposta_t2": kl_com_t2,
        "kl_prompt_t2": kls["prompt"],
        "kl_primeiro_t2": kls["primeiro"],
        "kl_tudo_t2": kls["tudo"],
        "kl_resposta_sem_t2": kl_sem_t2,
        "razao_t2": razao,
        "t2_esperado": float(temperatura ** 2),
        "t2_bate": razao is not None and abs(razao - (temperatura ** 2)) < 1e-3,
        "complecao_amostra": complecao[:48],
    }


def _loop(
    pares: list[dict],
    *,
    fn,
    passos: int,
    lr: float,
    device: str,
    seed: int,
    tipo: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    torch.manual_seed(seed)
    model, tok = carregar_aluno(device)
    opt = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=lr)
    losses: list[float] = []
    model.train()
    for i in range(passos):
        ex = pares[i % len(pares)]
        loss = fn(model, tok, ex)
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
    out = {"model": model, "tokenizer": tok, "losses": losses, "passos": passos, "tipo": tipo}
    out.update(extra)
    return out


def treinar_sequencia(
    pares: list[dict],
    *,
    passos: int = 8,
    lr: float = 2e-4,
    device: str = "cpu",
    seed: int = 0,
) -> dict[str, Any]:
    def fn(model, tok, ex):
        return loss_sequencia(model, tok, ex["prompt"], ex["complecao"], device)

    return _loop(pares, fn=fn, passos=passos, lr=lr, device=device, seed=seed, tipo="sequencia", extra={})


def treinar_logits(
    pares: list[dict],
    teacher,
    tok_t,
    *,
    temperatura: float = 2.0,
    passos: int = 8,
    lr: float = 2e-4,
    device: str = "cpu",
    seed: int = 1,
    modo_mascara: ModoMascara = "resposta",
) -> dict[str, Any]:
    teacher.eval()

    def fn(model, tok, ex):
        return loss_logits(
            model,
            teacher,
            tok,
            ex["prompt"],
            ex["complecao"],
            temperatura=temperatura,
            device=device,
            modo_mascara=modo_mascara,
        )

    return _loop(
        pares,
        fn=fn,
        passos=passos,
        lr=lr,
        device=device,
        seed=seed,
        tipo="logits",
        extra={"temperatura": temperatura, "modo_mascara": modo_mascara},
    )


def treinar_mista(
    pares: list[dict],
    teacher,
    tok_t,
    *,
    temperatura: float = 2.0,
    alpha: float = 0.5,
    passos: int = 8,
    lr: float = 2e-4,
    device: str = "cpu",
    seed: int = 3,
    modo_mascara: ModoMascara = "resposta",
) -> dict[str, Any]:
    teacher.eval()

    def fn(model, tok, ex):
        return loss_mista(
            model,
            teacher,
            tok,
            ex["prompt"],
            ex["complecao"],
            temperatura=temperatura,
            alpha=alpha,
            device=device,
            modo_mascara=modo_mascara,
        )

    return _loop(
        pares,
        fn=fn,
        passos=passos,
        lr=lr,
        device=device,
        seed=seed,
        tipo="mista",
        extra={"temperatura": temperatura, "alpha": alpha, "modo_mascara": modo_mascara},
    )
