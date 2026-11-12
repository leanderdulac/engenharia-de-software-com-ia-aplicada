#!/usr/bin/env python3
"""Labs A9 → ``modulo-a9/saidas/ca9.json``.

    python modulo-a9/lab/lab_a9.py

    TRILHA_A9_PASSOS=3
    TRILHA_A9_SEM_GRPO=1     só REINFORCE + hacking (sem SmolLM2)
    TRILHA_A9_SEM_BETA=1     não roda o smoke beta>0
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

import torch  # noqa: E402

from ambiente import coletar_ambiente  # noqa: E402
from hacking import demonstrar  # noqa: E402
from reinforce import comparar_baseline  # noqa: E402
from tarefas import pares_avaliacao, pares_treino, recompensa_exata, recompensa_hack_digito, split_ok  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca9.json"


def _serializavel(x):
    if isinstance(x, dict):
        return {k: _serializavel(v) for k, v in x.items() if k not in {"trainer", "tokenizer"}}
    if isinstance(x, list):
        return [_serializavel(v) for v in x]
    if isinstance(x, float):
        return x
    return x


def _libs() -> dict:
    out: dict = {}
    for name in ("trl", "peft", "datasets"):
        try:
            m = __import__(name)
            out[name] = getattr(m, "__version__", "sem_versao")
        except Exception as e:  # pragma: no cover
            out[name] = f"ausente: {type(e).__name__}"
    return out


def main() -> None:
    t0 = time.perf_counter()
    payload: dict = {
        "ambiente": coletar_ambiente(),
        "libs": _libs(),
        "honestidade": {
            "a7": "nao_publicado",
            "m09_grpo_demo": "nao_copia; aquele script nao atualiza pesos",
            "sft_trilha": "ausente; GRPO parte do SmolLM2-135M base + LoRA",
            "t4_colab": "nao_calibrado",
        },
    }

    print("=== A9.1 REINFORCE brinquedo ===")
    payload["a9_1"] = comparar_baseline(passos=200, semente=0)
    c, s = payload["a9_1"]["com_baseline"], payload["a9_1"]["sem_baseline"]
    print(
        f"  com baseline fim={c['recompensa_media_fim']:.3f} p*={c['p_otima']:.3f} "
        f"sem fim={s['recompensa_media_fim']:.3f} p*={s['p_otima']:.3f}"
    )

    print("=== A9.2 reward hacking (sinal, sem treino) ===")
    payload["a9_2"] = demonstrar()
    print(f"  divergencias={payload['a9_2']['n_divergencias']} exata={payload['a9_2']['exata']} hack={payload['a9_2']['hack_digito']}")

    skip = bool(os.environ.get("TRILHA_A9_SEM_GRPO"))
    if skip:
        payload["a9_3"] = {"status": "pulado_env"}
        payload["a9_4"] = {"status": "pulado_env"}
        print("=== GRPO pulado (TRILHA_A9_SEM_GRPO) ===")
    else:
        from treinar_grpo import MODELO, gerar_e_pontuar, treinar_grpo

        treino, ev = pares_treino(), pares_avaliacao()
        print("=== A9.3 GRPOTrainer (beta=0, atualiza LoRA) ===")
        t3 = time.perf_counter()
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok0 = AutoTokenizer.from_pretrained(MODELO)
        if tok0.pad_token is None:
            tok0.pad_token = tok0.eos_token
        base = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
        base.eval()
        antes = gerar_e_pontuar(base, tok0, ev, recompensa_exata)
        antes_tr = gerar_e_pontuar(base, tok0, treino, recompensa_exata)
        print(
            f"  eval antes r_media={antes['recompensa_media']:.3f} acertos={antes['n_acertos']}/{antes['n']} "
            f"treino_antes={antes_tr['recompensa_media']:.3f}"
        )

        grpo = treinar_grpo(treino, recompensa_exata, beta=0.0)
        trainer = grpo.pop("trainer")
        tok = grpo.pop("tokenizer")
        device_s = str(next(trainer.model.parameters()).device)
        depois = gerar_e_pontuar(trainer.model, tok, ev, recompensa_exata, device=device_s)
        depois_tr = gerar_e_pontuar(trainer.model, tok, treino, recompensa_exata, device=device_s)
        grpo["split"] = split_ok()
        grpo["eval_antes"] = {k: antes[k] for k in ("n", "recompensa_media", "n_acertos")}
        grpo["eval_depois"] = {k: depois[k] for k in ("n", "recompensa_media", "n_acertos")}
        grpo["eval_depois_amostra"] = depois["amostra"]
        grpo["eval_antes_amostra"] = antes["amostra"]
        grpo["treino_antes"] = {k: antes_tr[k] for k in ("n", "recompensa_media", "n_acertos")}
        grpo["treino_depois"] = {k: depois_tr[k] for k in ("n", "recompensa_media", "n_acertos")}
        zeros = [m.get("frac_reward_zero_std") for m in grpo.get("log_history", []) if "frac_reward_zero_std" in m]
        grpo["frac_reward_zero_std"] = [float(z) for z in zeros]
        if depois["recompensa_media"] <= antes["recompensa_media"] + 1e-12:
            grpo["por_que_nao_subiu"] = (
                f"eval {antes['recompensa_media']:.3f}→{depois['recompensa_media']:.3f} "
                f"(acertos {antes['n_acertos']}/{antes['n']} → {depois['n_acertos']}/{depois['n']}); "
                f"frac_reward_zero_std={grpo['frac_reward_zero_std']}; "
                "3 passos, G=2, SmolLM2-135M base+LoRA. "
                "GRPOTrainer.train() rodou (atualiza_pesos); se o grupo for homogêneo o Â some."
            )
        else:
            grpo["por_que_nao_subiu"] = None
        grpo["segundos"] = round(time.perf_counter() - t3, 3)
        payload["a9_3"] = _serializavel(grpo)
        print(
            f"  train_loss={grpo.get('train_loss')} rewards_log={grpo.get('rewards_log')} "
            f"eval {antes['recompensa_media']:.3f}→{depois['recompensa_media']:.3f} "
            f"treino_depois={depois_tr['recompensa_media']:.3f}"
        )
        del trainer

        print("=== A9.4 GRPO beta>0 (fumaça) + hack no mesmo gerado ===")
        t4 = time.perf_counter()
        fam: dict = {}
        if os.environ.get("TRILHA_A9_SEM_BETA"):
            fam["beta_pos"] = {"status": "pulado_env"}
        else:
            try:
                g2 = treinar_grpo(
                    treino[:4],
                    recompensa_exata,
                    beta=0.04,
                    max_steps=1,
                    output_dir=AQUI.parent / "saidas" / "runs" / "grpo-beta",
                )
                g2.pop("trainer", None)
                g2.pop("tokenizer", None)
                fam["beta_pos"] = {
                    "status": "ok",
                    "beta": 0.04,
                    "max_steps": 1,
                    "train_loss": g2.get("train_loss"),
                    "kl_log": g2.get("kl_log"),
                    "rewards_log": g2.get("rewards_log"),
                    "nota": "1 passo; nao comparar qualidade com beta=0 de 3 passos",
                }
            except Exception as e:
                fam["beta_pos"] = {"status": "falhou", "beta": 0.04, "erro": f"{type(e).__name__}: {e}"}
        # hacking nos gerados do eval (depois do GRPO beta=0 já medido; aqui no base)
        hack_base = gerar_e_pontuar(base, tok0, ev, recompensa_hack_digito)
        exact_base = antes
        fam["hack_vs_exata_no_base"] = {
            "exata_media": exact_base["recompensa_media"],
            "hack_media": hack_base["recompensa_media"],
            "nota": "no base, dígito qualquer já pontua no hack; a exata exige o inteiro ouro",
        }
        fam["segundos"] = round(time.perf_counter() - t4, 3)
        payload["a9_4"] = fam
        print("  beta_pos", fam.get("beta_pos", {}).get("status"), "hack_base", hack_base["recompensa_media"])
        del base

    payload["a9_5_t4"] = {
        "status": "nao_calibrado",
        "motivo": "CPU sem CUDA; GRPO G grande / T4 / IC do retido e alvo de Colab",
    }
    payload["segundos_total"] = round(time.perf_counter() - t0, 3)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
