#!/usr/bin/env python3
"""Labs A10 → ``modulo-a10/saidas/ca10.json``.

    python modulo-a10/lab/lab_a10.py

    TRILHA_A10_PASSOS=8
    TRILHA_A10_N_EVAL=60
    TRILHA_A10_SEM_DESTILAR=1   só gera/filtra (sem LoRA)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
A2_LAB = AQUI.parents[1] / "modulo-a2" / "lab"
sys.path.insert(0, str(A2_LAB))
sys.path.insert(0, str(AQUI.parents[1] / "modulo-a5" / "lab"))

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from ambiente import coletar_ambiente  # noqa: E402
from destilar import diagnosticar_kl, treinar_logits, treinar_mista, treinar_sequencia  # noqa: E402
from pi_sft import manifesto as manifesto_pi_sft  # noqa: E402
from filtro import filtrar  # noqa: E402
from licencas import ALUNO, PROFESSOR, manifesto  # noqa: E402
from medir import avaliar, gerar_complecoes, rss_mb  # noqa: E402
from tarefas import pares_avaliacao, pares_treino, split_ok  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca10.json"


def _serializavel(x):
    if isinstance(x, dict):
        return {k: _serializavel(v) for k, v in x.items() if k not in {"model", "tokenizer", "trainer"}}
    if isinstance(x, list):
        return [_serializavel(v) for v in x]
    if isinstance(x, float):
        return x
    return x


def _pontuar(d: dict) -> dict:
    keep = ("n", "acuracia", "n_acertos", "latencia_p50_s", "pegada_mb", "rss_processo_mb")
    return {k: d.get(k) for k in keep}


def _carregar(modelo: str, device: str = "cpu"):
    tok = AutoTokenizer.from_pretrained(modelo)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    m = AutoModelForCausalLM.from_pretrained(modelo, dtype=torch.float32)
    m.to(device)
    m.eval()
    return m, tok


def main() -> None:
    t0 = time.perf_counter()
    device = "cpu"
    passos = int(os.environ.get("TRILHA_A10_PASSOS", "8"))
    payload: dict = {
        "ambiente": coletar_ambiente(),
        "honestidade": {
            "a5_a7": "A5 publicado (π_SFT opcional); A7 esqueleto",
            "ponto_partida": manifesto_pi_sft(),
            "t4_colab": "nao_calibrado",
            "esquecimento": "nao_medido (só a tarefa de soma; aula discute retenção)",
        },
        "licencas": manifesto(),
        "rss_inicio_mb": rss_mb(),
    }

    treino, ev = pares_treino(), pares_avaliacao()
    print(f"=== A10.1 professor {PROFESSOR} gera + filtro ===")
    t1 = time.perf_counter()
    teacher, tok_t = _carregar(PROFESSOR, device)
    mesmo_tok = tok_t("2+2=", add_special_tokens=False).input_ids == AutoTokenizer.from_pretrained(ALUNO)(
        "2+2=", add_special_tokens=False
    ).input_ids
    payload["licencas"]["mesmo_tokenizer"] = bool(mesmo_tok)
    gerados = gerar_complecoes(teacher, tok_t, treino, device=device)
    filt = filtrar(gerados)
    print(
        f"  gerados={filt['n_gerados']} aceitos={filt['n_aceitos']} "
        f"taxa={filt['taxa_aceite']:.3f} mesmo_tok={mesmo_tok}"
    )
    ev_prof = avaliar(teacher, tok_t, ev, device=device)
    print(f"  professor eval acc={ev_prof['acuracia']:.3f} p50={ev_prof['latencia_p50_s']:.3f}s pegada={ev_prof['pegada_mb']}")
    payload["a10_1"] = {
        "professor": PROFESSOR,
        "split": split_ok(),
        "filtro": {k: filt[k] for k in ("n_gerados", "n_aceitos", "n_rejeitados", "taxa_aceite")},
        "rejeitados_amostra": filt["rejeitados_amostra"],
        "aceitos_amostra": [
            {"prompt": a["prompt"].strip(), "ouro": a["answer"], "complecao": a["complecao"][:40]}
            for a in filt["aceitos"][:3]
        ],
        "eval_professor": {**_pontuar(ev_prof), "amostra": ev_prof["amostra"]},
        "segundos": round(time.perf_counter() - t1, 3),
    }

    print(f"=== A10.2 aluno original {ALUNO} ===")
    t2 = time.perf_counter()
    aluno0, tok_a = _carregar(ALUNO, device)
    ev_al = avaliar(aluno0, tok_a, ev, device=device)
    print(f"  aluno_base acc={ev_al['acuracia']:.3f} p50={ev_al['latencia_p50_s']:.3f}s pegada={ev_al['pegada_mb']}")
    payload["a10_2"] = {
        "aluno": ALUNO,
        "eval": {**_pontuar(ev_al), "amostra": ev_al["amostra"]},
        "segundos": round(time.perf_counter() - t2, 3),
    }
    del aluno0

    skip = bool(os.environ.get("TRILHA_A10_SEM_DESTILAR"))
    aceitos = filt["aceitos"]
    if skip or not aceitos:
        payload["a10_3"] = {
            "status": "pulado" if skip else "sem_aceitos",
            "n_aceitos": len(aceitos),
        }
        payload["a10_4"] = {"status": "pulado"}
        payload["a10_4c"] = {"status": "pulado"}
        print("=== destilação pulada ===")
    else:
        print(f"=== A10.3 destilação por resposta (CE, {passos} passos, n={len(aceitos)}) ===")
        t3 = time.perf_counter()
        seq = treinar_sequencia(aceitos, passos=passos, device=device)
        ev_seq = avaliar(seq["model"], seq["tokenizer"], ev, device=device)
        print(f"  seq acc={ev_seq['acuracia']:.3f} loss_fim={seq['losses'][-1]:.4f}")
        payload["a10_3"] = {
            "tipo": "sequencia",
            "passos": passos,
            "n_pares": len(aceitos),
            "losses": seq["losses"],
            "eval": {**_pontuar(ev_seq), "amostra": ev_seq["amostra"]},
            "segundos": round(time.perf_counter() - t3, 3),
        }
        del seq

        print(f"=== A10.4 destilação por logits (T=2, {passos} passos, máscara=resposta) ===")
        t4 = time.perf_counter()
        aluno_diag, tok_diag = _carregar(ALUNO, device)
        diag = diagnosticar_kl(
            aluno_diag,
            teacher,
            tok_diag,
            aceitos[0]["prompt"],
            aceitos[0]["complecao"],
            temperatura=2.0,
            device=device,
        )
        del aluno_diag
        print(
            "  diag shift_alinhado={shift} inclui_prompt={inc} "
            "t2_bate={t2} n_comp={nc} kl_resp={kr:.4f} kl_prompt={kp:.4f}".format(
                shift=diag["shift_alinhado"],
                inc=diag["mascara_inclui_prompt"],
                t2=diag["t2_bate"],
                nc=diag["n_complecao"],
                kr=diag["kl_resposta_t2"],
                kp=diag["kl_prompt_t2"],
            )
        )
        kd = treinar_logits(aceitos, teacher, tok_t, temperatura=2.0, passos=passos, device=device)
        ev_kd = avaliar(kd["model"], kd["tokenizer"], ev, device=device)
        print(f"  logits T=2 acc={ev_kd['acuracia']:.3f} kl_fim={kd['losses'][-1]:.4f}")
        payload["a10_4"] = {
            "tipo": "logits",
            "temperatura": 2.0,
            "modo_mascara": "resposta",
            "passos": passos,
            "n_pares": len(aceitos),
            "diagnostico": diag,
            "losses": kd["losses"],
            "eval": {**_pontuar(ev_kd), "amostra": ev_kd["amostra"]},
            "segundos": round(time.perf_counter() - t4, 3),
        }
        del kd

        print("=== A10.4b curva T (2 passos, T=4) ===")
        kd4 = treinar_logits(aceitos, teacher, tok_t, temperatura=4.0, passos=min(2, passos), device=device, seed=2)
        payload["a10_4b_T"] = {
            "temperatura": 4.0,
            "passos": min(2, passos),
            "losses": kd4["losses"],
            "nota": "fumaça da curva T; não compete com T=2 de 8 passos",
        }
        del kd4

        print(f"=== A10.4c perda mista α·CE+(1-α)·T²·KL (α=0,5, {passos} passos) ===")
        t4c = time.perf_counter()
        mix = treinar_mista(
            aceitos, teacher, tok_t, temperatura=2.0, alpha=0.5, passos=passos, device=device
        )
        ev_mix = avaliar(mix["model"], mix["tokenizer"], ev, device=device)
        print(f"  mista α=0.5 acc={ev_mix['acuracia']:.3f} loss_fim={mix['losses'][-1]:.4f}")
        payload["a10_4c"] = {
            "tipo": "mista",
            "temperatura": 2.0,
            "alpha": 0.5,
            "modo_mascara": "resposta",
            "passos": passos,
            "n_pares": len(aceitos),
            "losses": mix["losses"],
            "eval": {**_pontuar(ev_mix), "amostra": ev_mix["amostra"]},
            "segundos": round(time.perf_counter() - t4c, 3),
            "formula": "alpha * CE(labels) + (1-alpha) * T^2 * KL(p_T || p_S)",
        }
        del mix

    del teacher

    payload["a10_5"] = {
        "tabela": {
            "professor": payload["a10_1"]["eval_professor"],
            "aluno_original": payload["a10_2"]["eval"],
            "aluno_sequencia": payload.get("a10_3", {}).get("eval"),
            "aluno_logits": payload.get("a10_4", {}).get("eval"),
            "aluno_mista": payload.get("a10_4c", {}).get("eval"),
        },
        "nota": (
            "acurácia = primeiro inteiro == ouro no hold-out. "
            "latência p50 = s/prompt greedy 8 tokens. pegada = get_memory_footprint. "
            "não é ranking universal nem IC."
        ),
    }
    payload["a10_6_t4"] = {
        "status": "nao_calibrado",
        "motivo": "CPU sem CUDA; T4 / vLLM / custo/1k são alvo de Colab",
    }
    payload["rss_fim_mb"] = rss_mb()
    payload["segundos_total"] = round(time.perf_counter() - t0, 3)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(_serializavel(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
