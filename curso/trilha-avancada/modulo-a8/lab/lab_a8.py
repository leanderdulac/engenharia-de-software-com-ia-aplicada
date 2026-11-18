#!/usr/bin/env python3
"""Labs A8 → ``modulo-a8/saidas/ca8.json``.

    python modulo-a8/lab/lab_a8.py

    TRILHA_A8_PASSOS=8          passos DPO (CPU)
    TRILHA_A8_SEM_TREINO=1      só perdas no papel + comprimento (sem SmolLM2)
    TRILHA_A8_SEM_EXPERIMENTAL=1  não instancia ORPO/SimPO
    TRILHA_A8_SEM_KTO=1         não instancia KTOTrainer
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
from logps import avaliar_pares, tensores_do_relatorio  # noqa: E402
from pares import (  # noqa: E402
    conferir_fronteira,
    estatistica_comprimento,
    pares_avaliacao,
    pares_dpo,
    pares_kto,
    pares_treino,
    split_ok,
)
from perdas import exemplo_numerico_aula, tabela_no_lote  # noqa: E402

SAIDA = AQUI.parent / "saidas" / "ca8.json"


def _serializavel(x):
    if isinstance(x, dict):
        return {k: _serializavel(v) for k, v in x.items() if k not in {"trainer", "tokenizer", "linhas"}}
    if isinstance(x, list):
        return [_serializavel(v) for v in x]
    if isinstance(x, float):
        return x
    return x


def main() -> None:
    t0 = time.perf_counter()
    pares = pares_dpo()
    treino = pares_treino()
    avaliacao = pares_avaliacao()
    def _libs() -> dict:
        out: dict = {}
        for name in ("trl", "peft", "datasets"):
            try:
                m = __import__(name)
                out[name] = getattr(m, "__version__", "sem_versao")
            except Exception as e:  # pragma: no cover
                out[name] = f"ausente: {type(e).__name__}"
        return out

    payload: dict = {
        "ambiente": coletar_ambiente(),
        "libs": _libs(),
        "honestidade": {
            "a5_a6": "nao_publicados",
            "sft_trilha": "ausente; DPO parte do SmolLM2-135M base + LoRA",
            "jsonl_m09": "nao_copiado; pares originais no padrao JSON vs prosa / virgula decimal",
            "t4_colab": "nao_calibrado",
        },
        "a8_1": {
            "n_pares": len(pares),
            "split": split_ok(),
            "comprimento": estatistica_comprimento(pares),
            "comprimento_treino": estatistica_comprimento(treino),
            "comprimento_eval": estatistica_comprimento(avaliacao),
            "exemplo_aula": exemplo_numerico_aula(),
        },
    }
    print("=== A8.1 pares e comprimento ===")
    c = payload["a8_1"]["comprimento"]
    sp = payload["a8_1"]["split"]
    print(
        f"  n={c['n']} treino={sp['n_treino']} eval={sp['n_eval']} "
        f"disjuntos={sp['prompts_disjuntos']} "
        f"chosen_chars={c['chosen_chars_medio']:.1f} rejected_chars={c['rejected_chars_medio']:.1f} "
        f"razao={c['razao_rejected_sobre_chosen']:.2f}"
    )

    skip = bool(os.environ.get("TRILHA_A8_SEM_TREINO"))
    if skip:
        payload["a8_2"] = {"status": "pulado_env"}
        payload["a8_3"] = {"status": "pulado_env"}
        payload["a8_4"] = {"status": "pulado_env"}
        print("=== treino pulado (TRILHA_A8_SEM_TREINO) ===")
    else:
        from treinar import tentar_experimental, tentar_kto, treinar_dpo

        print("=== A8.2 DPO LoRA (TRL) ===")
        t2 = time.perf_counter()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from treinar import MODELO as ID_SMOL

        tok_ref = AutoTokenizer.from_pretrained(ID_SMOL)
        if tok_ref.pad_token is None:
            tok_ref.pad_token = tok_ref.eos_token
        fronteira = conferir_fronteira(tok_ref, pares)
        payload["a8_1"]["fronteira_tokenizer"] = fronteira
        print(f"  fronteira_ok={fronteira['ok']} falhas={fronteira['n_falhas']}")
        ref = AutoModelForCausalLM.from_pretrained(ID_SMOL, dtype=torch.float32)
        ref.eval()
        antes_tr = avaliar_pares(ref, tok_ref, treino, device="cpu")
        antes_ev = avaliar_pares(ref, tok_ref, avaliacao, device="cpu")
        print(
            f"  base treino preferencia_bruta={antes_tr['preferencia_bruta']:.3f} "
            f"eval preferencia_bruta={antes_ev['preferencia_bruta']:.3f}"
        )

        dpo = treinar_dpo(treino, pares_eval=avaliacao)
        trainer = dpo.pop("trainer")
        tok = dpo.pop("tokenizer")
        device_s = str(next(trainer.model.parameters()).device)
        print("=== A8.2b logps / margem vs base (eval hold-out) ===")
        depois_tr = avaliar_pares(trainer.model, tok, treino, device=device_s, modelo_ref=ref)
        depois_ev = avaliar_pares(trainer.model, tok, avaliacao, device=device_s, modelo_ref=ref)
        campos = ("n", "preferencia_bruta", "rewards_accuracies", "margem_media", "fracao_chosen_mais_curto")
        dpo["avaliacao_treino_base"] = {k: antes_tr[k] for k in campos}
        dpo["avaliacao_treino_depois"] = {k: depois_tr[k] for k in campos}
        dpo["avaliacao_eval_base"] = {k: antes_ev[k] for k in campos}
        dpo["avaliacao_eval_depois"] = {k: depois_ev[k] for k in campos}
        dpo["avaliacao_base"] = dpo["avaliacao_eval_base"]
        dpo["avaliacao_depois"] = dpo["avaliacao_eval_depois"]
        dpo["segundos"] = round(time.perf_counter() - t2, 3)
        payload["a8_2"] = _serializavel(dpo)
        print(
            f"  train_loss={dpo.get('train_loss')} aviso_prefixo={dpo.get('aviso_prefixo_trl')} "
            f"acc_treino={depois_tr['rewards_accuracies']:.3f} acc_eval={depois_ev['rewards_accuracies']:.3f} "
            f"margem_eval={depois_ev['margem_media']:.3f}"
        )

        tens = tensores_do_relatorio(depois_ev, device="cpu")
        tab = tabela_no_lote(
            tens["logp_w"],
            tens["logp_l"],
            tens["logp_w_ref"],
            tens["logp_l_ref"],
            tens["n_w"],
            tens["n_l"],
            beta_dpo=0.1,
        )
        from perdas import perda_dpo

        beta_scan = {
            str(b): float(
                perda_dpo(tens["logp_w"], tens["logp_l"], tens["logp_w_ref"], tens["logp_l_ref"], beta=b)
            )
            for b in (0.1, 0.5, 1.0)
        }
        payload["a8_3"] = {
            "perdas_no_mesmo_lote_depois_dpo": tab,
            "dpo_vs_beta": beta_scan,
            "nota": (
                "mesmos logps do hold-out; unidades diferentes (sigmoid vs quadrado vs SFT+OR); "
                "NAO e ranking de qualidade. SimPO/ORPO/KTO aqui sao formulas da aula; treino experimental e A8.4"
            ),
        }
        print("  perdas", {k: round(tab[k], 4) for k in ("dpo_sigmoid", "ipo", "simpo", "orpo", "kto")})

        print("=== A8.4 familia TRL (IPO/KTO estaveis; ORPO/SimPO experimental) ===")
        t4 = time.perf_counter()
        fam: dict = {"t4_colab": "nao_calibrado"}
        try:
            ipo_d = treinar_dpo(
                treino,
                pares_eval=None,
                max_steps=1,
                loss_type="ipo",
                output_dir=AQUI.parent / "saidas" / "runs" / "ipo-fumaca",
            )
            ipo_d.pop("trainer", None)
            ipo_d.pop("tokenizer", None)
            fam["ipo"] = {
                "status": "ok",
                "api": "trl.DPOTrainer loss_type=ipo (estavel)",
                "train_loss": ipo_d.get("train_loss"),
                "max_steps": 1,
                "nota": "1 passo para exercitar a API estavel; nao comparar train_loss com DPO de 8 passos",
            }
        except Exception as e:  # pragma: no cover
            fam["ipo"] = {
                "status": "falhou",
                "api": "trl.DPOTrainer loss_type=ipo (estavel)",
                "erro": f"{type(e).__name__}: {e}",
            }
        if os.environ.get("TRILHA_A8_SEM_KTO"):
            fam["kto"] = {"status": "pulado_env"}
        else:
            fam["kto"] = tentar_kto(pares_kto(treino), max_steps=int(os.environ.get("TRILHA_A8_PASSOS_KTO", "2")))
        if os.environ.get("TRILHA_A8_SEM_EXPERIMENTAL"):
            fam["orpo"] = {"status": "pulado_env", "api": "trl.experimental.orpo.ORPOTrainer"}
            fam["simpo"] = {"status": "pulado_env", "api": "trl.experimental.cpo.CPOTrainer"}
        else:
            fam.update(tentar_experimental(treino, max_steps=1))
        fam["segundos"] = round(time.perf_counter() - t4, 3)
        payload["a8_4"] = fam
        print(
            "  ipo",
            fam.get("ipo", {}).get("status"),
            "kto",
            fam.get("kto", {}).get("status"),
            "orpo",
            fam.get("orpo", {}).get("status"),
            "simpo",
            fam.get("simpo", {}).get("status"),
        )
        del trainer, ref

    payload["a8_5_t4"] = {
        "status": "nao_calibrado",
        "motivo": "esta VM nao tem CUDA; limiar CA8 rewards/accuracies>0.5 com IC e harness e alvo de T4/Colab",
    }
    payload["segundos_total"] = round(time.perf_counter() - t0, 3)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON → {SAIDA}  ({payload['segundos_total']} s)")


if __name__ == "__main__":
    main()
