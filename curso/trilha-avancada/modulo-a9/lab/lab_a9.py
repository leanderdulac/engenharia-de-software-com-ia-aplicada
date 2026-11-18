#!/usr/bin/env python3
"""Labs A9 → ``modulo-a9/saidas/ca9.json``.

    python modulo-a9/lab/lab_a9.py

    TRILHA_A9_PASSOS=16
    TRILHA_A9_G=4
    TRILHA_A9_SEEDS=0,1,2
    TRILHA_A9_N_EVAL=80
    TRILHA_A9_SEM_GRPO=1     só REINFORCE + hacking
    TRILHA_A9_SEM_BETA=1     não compara beta>0
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

from ambiente import coletar_ambiente  # noqa: E402
from hacking import demonstrar  # noqa: E402
from reinforce import comparar_baseline  # noqa: E402
from pi_sft import manifesto as manifesto_pi_sft  # noqa: E402
from tarefas import (  # noqa: E402
    media_desvio,
    pares_avaliacao,
    pares_treino,
    recompensa_exata,
    recompensa_hack_digito,
    split_ok,
)

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


def _seeds() -> list[int]:
    raw = os.environ.get("TRILHA_A9_SEEDS", "0,1,2")
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _pontuar(d: dict) -> dict:
    return {k: d[k] for k in ("n", "recompensa_media", "n_acertos")}


def _melhorou_claro(deltas: list[float]) -> dict:
    st = media_desvio(deltas)
    m, d = st["media"], st["desvio"]
    if m is None:
        return {**st, "claro": False, "nota": "sem deltas"}
    # n=3: a média precisa ser positiva e maior que o desvio amostral.
    claro = m > 0 and d is not None and m >= max(d, 0.03)
    return {
        **st,
        "claro": claro,
        "nota": (
            "média do delta > desvio e ≥ 0,03"
            if claro
            else "sem melhora clara: média do delta da ordem do desvio, ≤0, ou < 0,03 (n_eval=80, n_seeds=3, sem IC)"
        ),
    }


def main() -> None:
    t0 = time.perf_counter()
    payload: dict = {
        "ambiente": coletar_ambiente(),
        "libs": _libs(),
        "honestidade": {
            "a7": "nao_publicado",
            "m09_grpo_demo": "nao_copia; aquele script nao atualiza pesos",
            "sft_trilha": "π_SFT do A5 se adapter existir; TRILHA_PI_SFT=0 força o base",
            "ponto_partida": manifesto_pi_sft(),
            "t4_colab": "nao_calibrado",
            "eval_greedy": "antes é o base (std=0 entre seeds); variação é o treino",
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
    print(
        f"  divergencias={payload['a9_2']['n_divergencias']} "
        f"exata={payload['a9_2']['exata']} hack={payload['a9_2']['hack_digito']}"
    )

    skip = bool(os.environ.get("TRILHA_A9_SEM_GRPO"))
    if skip:
        payload["a9_3"] = {"status": "pulado_env"}
        payload["a9_4"] = {"status": "pulado_env"}
        print("=== GRPO pulado (TRILHA_A9_SEM_GRPO) ===")
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        from treinar_grpo import MODELO, gerar_e_pontuar, treinar_grpo

        treino, ev = pares_treino(), pares_avaliacao()
        passos = int(os.environ.get("TRILHA_A9_PASSOS", "16"))
        g_grp = int(os.environ.get("TRILHA_A9_G", "4"))
        seeds = _seeds()
        print(
            f"=== A9.3 GRPOTrainer beta=0  G={g_grp} passos={passos} "
            f"seeds={seeds} n_eval={len(ev)} n_treino={len(treino)} ==="
        )
        t3 = time.perf_counter()
        tok0 = AutoTokenizer.from_pretrained(MODELO)
        if tok0.pad_token is None:
            tok0.pad_token = tok0.eos_token
        tok0.padding_side = "left"
        base = AutoModelForCausalLM.from_pretrained(MODELO, dtype=torch.float32)
        base.eval()
        antes = gerar_e_pontuar(base, tok0, ev, recompensa_exata)
        antes_tr = gerar_e_pontuar(base, tok0, treino, recompensa_exata)
        print(
            f"  eval_antes r={antes['recompensa_media']:.3f} "
            f"acertos={antes['n_acertos']}/{antes['n']} treino_antes={antes_tr['recompensa_media']:.3f}"
        )

        corridas = []
        for seed in seeds:
            ts = time.perf_counter()
            print(f"  -- seed {seed} --")
            grpo = treinar_grpo(
                treino,
                recompensa_exata,
                beta=0.0,
                max_steps=passos,
                num_generations=g_grp,
                seed=seed,
            )
            trainer = grpo.pop("trainer")
            tok = grpo.pop("tokenizer")
            device_s = str(next(trainer.model.parameters()).device)
            depois = gerar_e_pontuar(trainer.model, tok, ev, recompensa_exata, device=device_s)
            depois_tr = gerar_e_pontuar(trainer.model, tok, treino, recompensa_exata, device=device_s)
            delta = depois["recompensa_media"] - antes["recompensa_media"]
            row = {
                "seed": seed,
                "eval_depois": _pontuar(depois),
                "treino_depois": _pontuar(depois_tr),
                "delta_eval": delta,
                "rewards_log": grpo["rewards_log"],
                "frac_reward_zero_std": grpo["frac_reward_zero_std"],
                "n_passos_zero_std": grpo["n_passos_zero_std"],
                "frac_passos_zero_std": grpo["frac_passos_zero_std"],
                "train_loss": grpo["train_loss"],
                "atualiza_pesos": True,
                "amostra_depois": depois["amostra"][:4],
                "segundos": round(time.perf_counter() - ts, 3),
            }
            corridas.append(row)
            print(
                f"     eval {antes['recompensa_media']:.3f}→{depois['recompensa_media']:.3f} "
                f"delta={delta:+.3f} zero_std={grpo['n_passos_zero_std']}/{passos}"
            )
            del trainer
            del tok

        deltas = [r["delta_eval"] for r in corridas]
        depois_s = [r["eval_depois"]["recompensa_media"] for r in corridas]
        zeros_f = [r["frac_passos_zero_std"] for r in corridas if r["frac_passos_zero_std"] is not None]
        juizo = _melhorou_claro(deltas)
        payload["a9_3"] = {
            "beta": 0.0,
            "max_steps": passos,
            "num_generations": g_grp,
            "temperature": 1.0,
            "api": "trl.GRPOTrainer (estavel)",
            "atualiza_pesos": True,
            "split": split_ok(),
            "eval_antes": {**_pontuar(antes), "amostra": antes["amostra"][:4]},
            "treino_antes": _pontuar(antes_tr),
            "seeds": seeds,
            "corridas": corridas,
            "resumo": {
                "eval_antes": antes["recompensa_media"],
                "eval_depois": media_desvio(depois_s),
                "delta": juizo,
                "frac_passos_zero_std": media_desvio(zeros_f),
                "melhorou_claro": juizo["claro"],
            },
            "segundos": round(time.perf_counter() - t3, 3),
        }
        print(
            f"  resumo delta media={juizo['media']:.3f} desvio={juizo['desvio']:.3f} "
            f"claro={juizo['claro']}"
        )

        print("=== A9.4 GRPO beta=0.04 (KL) + hack no base ===")
        t4 = time.perf_counter()
        fam: dict = {}
        if os.environ.get("TRILHA_A9_SEM_BETA"):
            fam["beta_pos"] = {"status": "pulado_env"}
        else:
            try:
                ts = time.perf_counter()
                g2 = treinar_grpo(
                    treino,
                    recompensa_exata,
                    beta=0.04,
                    max_steps=passos,
                    num_generations=g_grp,
                    seed=0,
                    output_dir=AQUI.parent / "saidas" / "runs" / "grpo-beta",
                )
                trainer_b = g2.pop("trainer")
                tok_b = g2.pop("tokenizer")
                device_b = str(next(trainer_b.model.parameters()).device)
                depois_b = gerar_e_pontuar(trainer_b.model, tok_b, ev, recompensa_exata, device=device_b)
                del trainer_b
                del tok_b
                fam["beta_pos"] = {
                    "status": "ok",
                    "beta": 0.04,
                    "max_steps": passos,
                    "num_generations": g_grp,
                    "seed": 0,
                    "train_loss": g2.get("train_loss"),
                    "kl_log": g2.get("kl_log"),
                    "kl_max": g2.get("kl_max"),
                    "kl_n_nao_zero": g2.get("kl_n_nao_zero"),
                    "rewards_log": g2.get("rewards_log"),
                    "n_passos_zero_std": g2.get("n_passos_zero_std"),
                    "eval_depois": _pontuar(depois_b),
                    "delta_vs_base": depois_b["recompensa_media"] - antes["recompensa_media"],
                    "delta_vs_beta0_seed0": depois_b["recompensa_media"] - corridas[0]["eval_depois"]["recompensa_media"],
                    "nota": "mesmo G/passos/seed=0 que a primeira corrida beta=0; KL precisa aparecer no log",
                    "segundos": round(time.perf_counter() - ts, 3),
                }
            except Exception as e:
                fam["beta_pos"] = {"status": "falhou", "beta": 0.04, "erro": f"{type(e).__name__}: {e}"}
        hack_base = gerar_e_pontuar(base, tok0, ev[:20], recompensa_hack_digito)
        exact_sub = gerar_e_pontuar(base, tok0, ev[:20], recompensa_exata)
        fam["hack_vs_exata_no_base"] = {
            "n": 20,
            "exata_media": exact_sub["recompensa_media"],
            "hack_media": hack_base["recompensa_media"],
            "nota": "no base, dígito qualquer já pontua no hack; a exata exige o inteiro ouro",
        }
        fam["segundos"] = round(time.perf_counter() - t4, 3)
        payload["a9_4"] = fam
        bp = fam.get("beta_pos", {})
        print(
            "  beta_pos",
            bp.get("status"),
            "kl_max",
            bp.get("kl_max"),
            "kl_n_nao_zero",
            bp.get("kl_n_nao_zero"),
            "hack_base",
            hack_base["recompensa_media"],
        )
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
