"""Dois adapters no mesmo base: Amplitude (π_SFT) e soma curta."""

from __future__ import annotations

from typing import Any

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from pi_sft import MODELO, resolver
from sft_lora import greedy

SOMA_PARES = (
    ("2+2=", "4"),
    ("3+4=", "7"),
    ("5+1=", "6"),
    ("10+2=", "12"),
)


def _tok():
    tok = AutoTokenizer.from_pretrained(MODELO)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def _peft_soma():
    return LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )


def treinar_soma(passos: int = 24, lr: float = 2e-4) -> Any:
    tok = _tok()
    m = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    m = get_peft_model(m, _peft_soma())
    m.train()
    opt = torch.optim.AdamW((p for p in m.parameters() if p.requires_grad), lr=lr)
    itens = []
    for p, a in SOMA_PARES:
        ids = tok(p + a + (tok.eos_token or ""), add_special_tokens=False).input_ids
        n_p = len(tok(p, add_special_tokens=False).input_ids)
        lab = [-100] * n_p + ids[n_p:]
        itens.append({"input_ids": ids, "labels": lab})
    for t in range(passos):
        it = itens[t % len(itens)]
        opt.zero_grad(set_to_none=True)
        loss = m(
            input_ids=torch.tensor([it["input_ids"]]),
            labels=torch.tensor([it["labels"]]),
        ).loss
        loss.backward()
        opt.step()
    return m, tok, float(loss.detach())


def comparar(passos_soma: int = 24) -> dict[str, Any]:
    p = resolver()
    if p is None:
        return {"status": "sem_pi_sft"}
    soma, tok, loss_soma = treinar_soma(passos=passos_soma)
    base = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
    duo = PeftModel.from_pretrained(base, str(p), adapter_name="amplitude")
    tmp = "/tmp/trilha-a6-soma"
    soma.save_pretrained(tmp)
    del soma
    duo.load_adapter(tmp, adapter_name="soma")

    def _gen(nome: str, prompt: str) -> str:
        duo.set_adapter(nome)
        duo.eval()
        with torch.no_grad():
            return greedy(duo, tok, prompt, max_novos=16)

    json_p = "### assistant\n"
    # prefixo A4 mínimo para disparar o JSON
    from mascarar_sft import renderizar
    from dialogos_amplitude import SYSTEM, dialogos_eval

    d0 = dialogos_eval()[0]
    pref_json, _ = renderizar(d0["user"], "", system=SYSTEM)
    out = {
        "status": "ok",
        "loss_soma": loss_soma,
        "amplitude_no_json": _gen("amplitude", pref_json),
        "soma_no_json": _gen("soma", pref_json),
        "amplitude_em_2mais2": _gen("amplitude", "2+2="),
        "soma_em_2mais2": _gen("soma", "2+2="),
        "json_p": json_p,
    }
    ouro = d0["assistant"]
    out["amplitude_json_ok"] = ouro in out["amplitude_no_json"] or out["amplitude_no_json"].strip().startswith("{")
    out["soma_comeca_4"] = out["soma_em_2mais2"].strip().startswith("4")
    return out
