"""SFT LoRA só no assistant. Tracking local (sem W&B). GSM8K/Dolly não baixados."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from mascarar_sft import renderizar
from pi_sft import MODELO, PI_SFT_PADRAO

PROBES_GERAL = (
    "2+2=",
    "The capital of France is",
)


def tokenizer(modelo: str = MODELO):
    tok = AutoTokenizer.from_pretrained(modelo)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    return tok


def montar_peft(model):
    cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )
    return get_peft_model(model, cfg)


def carregar_aluno(device: str = "cpu"):
    m = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    m = montar_peft(m)
    m.to(device)
    return m


def loss_item(model, item: dict, *, so_assistant: bool) -> torch.Tensor:
    ids = torch.tensor([item["input_ids"]], device=next(model.parameters()).device)
    lab = item["labels"] if so_assistant else item["input_ids"]
    labels = torch.tensor([lab], device=ids.device)
    return model(input_ids=ids, labels=labels).loss


@torch.no_grad()
def greedy(model, tok, prefixo: str, *, max_novos: int = 48) -> str:
    device = next(model.parameters()).device
    lado = tok.padding_side
    tok.padding_side = "left"
    enc = tok(prefixo, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    n = enc["input_ids"].shape[1]
    out = model.generate(
        **enc,
        max_new_tokens=max_novos,
        do_sample=False,
        pad_token_id=tok.pad_token_id,
    )
    tok.padding_side = lado
    return tok.decode(out[0, n:], skip_special_tokens=True)


def exact_match(gerado: str, ouro: str) -> bool:
    g = gerado.strip().splitlines()[0].strip() if gerado.strip() else ""
    return g == ouro.strip()


def avaliar_dialogos(model, tok, dialogos: list[dict], *, system: str | None) -> dict[str, Any]:
    n_ok = 0
    linhas = []
    for d in dialogos:
        prefixo, _ = renderizar(d["user"], "", system=system)
        gerado = greedy(model, tok, prefixo)
        ok = exact_match(gerado, d["assistant"])
        n_ok += int(ok)
        linhas.append({"user": d["user"], "ouro": d["assistant"], "gerado": gerado[:200], "ok": ok})
    return {"n": len(dialogos), "n_ok": n_ok, "acuracia": n_ok / max(len(dialogos), 1), "linhas": linhas}


def probes_geral(model, tok) -> dict[str, str]:
    return {p: greedy(model, tok, p, max_novos=12) for p in PROBES_GERAL}


def treinar_sft(
    itens: list[dict],
    *,
    passos: int = 32,
    lr: float = 2e-4,
    so_assistant: bool = True,
    seed: int = 0,
    device: str = "cpu",
    salvar_em=None,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    tok = tokenizer()
    model = carregar_aluno(device)
    model.train()
    opt = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=lr)
    hist: list[float] = []
    for t in range(passos):
        item = itens[t % len(itens)]
        opt.zero_grad(set_to_none=True)
        loss = loss_item(model, item, so_assistant=so_assistant)
        loss.backward()
        opt.step()
        hist.append(float(loss.detach()))
    destino = None
    if salvar_em is not None:
        destino = str(salvar_em)
        Path_salvar = Path(salvar_em)
        Path_salvar.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(Path_salvar)
        leia = Path_salvar / "README.md"
        leia.write_text(
            "# π_SFT\n\nAdapter LoRA (PEFT) do lab A5 sobre "
            "`HuggingFaceTB/SmolLM2-135M`. Tokenizer **não** vai neste "
            "diretório — carregue o do card. A8/A9/A10 leem "
            "`adapter_config.json`, salvo `TRILHA_PI_SFT=0`.\n",
            encoding="utf-8",
        )
    n_treino = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    return {
        "passos": passos,
        "lr": lr,
        "so_assistant": so_assistant,
        "seed": seed,
        "loss_ini": hist[0] if hist else None,
        "loss_fim": hist[-1] if hist else None,
        "loss_min": min(hist) if hist else None,
        "caiu": bool(hist) and hist[-1] < hist[0],
        "historico": hist,
        "n_params_treino": n_treino,
        "n_params_total": n_total,
        "fracao_treino": n_treino / max(n_total, 1),
        "salvo_em": destino,
        "model": model,
        "tokenizer": tok,
    }


assert isinstance(PI_SFT_PADRAO, Path)
