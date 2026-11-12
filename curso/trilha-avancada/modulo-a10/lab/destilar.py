"""Destilação por resposta (CE na compleção) e por logits (KL com temperatura)."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from licencas import ALUNO


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


def carregar_aluno(device: str = "cpu"):
    tok = _tok(ALUNO)
    m = AutoModelForCausalLM.from_pretrained(ALUNO, dtype=torch.float32)
    m = _peft(m)
    m.to(device)
    return m, tok


def loss_sequencia(model, tok, prompt: str, complecao: str, device: str) -> torch.Tensor:
    f_ids, n_p = _ids(tok, prompt, complecao)
    if len(f_ids) <= n_p:
        return torch.zeros((), device=device, requires_grad=True)
    ids = torch.tensor([f_ids], device=device)
    logp = model(ids).logits[:, :-1, :].log_softmax(dim=-1)
    alvo = ids[:, 1:]
    ini = max(n_p - 1, 0)
    lp = logp[0, ini:, :].gather(1, alvo[0, ini:].unsqueeze(-1)).squeeze(-1)
    return -lp.mean()


def loss_logits(
    student,
    teacher,
    tok,
    prompt: str,
    complecao: str,
    *,
    temperatura: float,
    device: str,
) -> torch.Tensor:
    f_ids, n_p = _ids(tok, prompt, complecao)
    if len(f_ids) <= n_p:
        return torch.zeros((), device=device, requires_grad=True)
    ids = torch.tensor([f_ids], device=device)
    ini = max(n_p - 1, 0)
    with torch.no_grad():
        t = teacher(ids).logits[0, ini:-1, :] / temperatura
    s = student(ids).logits[0, ini:-1, :] / temperatura
    log_s = F.log_softmax(s, dim=-1)
    p_t = F.softmax(t, dim=-1)
    kl = F.kl_div(log_s, p_t, reduction="batchmean")
    return kl * (temperatura ** 2)


def treinar_sequencia(
    pares: list[dict],
    *,
    passos: int = 8,
    lr: float = 2e-4,
    device: str = "cpu",
    seed: int = 0,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    model, tok = carregar_aluno(device)
    opt = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=lr)
    losses: list[float] = []
    model.train()
    for i in range(passos):
        ex = pares[i % len(pares)]
        loss = loss_sequencia(model, tok, ex["prompt"], ex["complecao"], device)
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
    return {"model": model, "tokenizer": tok, "losses": losses, "passos": passos, "tipo": "sequencia"}


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
) -> dict[str, Any]:
    torch.manual_seed(seed)
    student, tok = carregar_aluno(device)
    # mesmo tokenizer (conferido no lab)
    opt = torch.optim.AdamW((p for p in student.parameters() if p.requires_grad), lr=lr)
    losses: list[float] = []
    student.train()
    teacher.eval()
    for i in range(passos):
        ex = pares[i % len(pares)]
        loss = loss_logits(
            student, teacher, tok, ex["prompt"], ex["complecao"], temperatura=temperatura, device=device
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
    return {
        "model": student,
        "tokenizer": tok,
        "losses": losses,
        "passos": passos,
        "temperatura": temperatura,
        "tipo": "logits",
    }
