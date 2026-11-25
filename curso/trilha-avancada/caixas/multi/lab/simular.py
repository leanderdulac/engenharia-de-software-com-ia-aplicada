#!/usr/bin/env python3
"""Simulação didática: um harness só versus produtor, revisor e falsificador.

Não é um LLM e não chama API. O mesmo plano (seed) roda nos dois arranjos.

- U: um harness escreve código e, se o teste aperta, pode reescrever o teste.
- T: três contratos. O produtor não grava o teste (a escrita é barrada).
  O revisor lê o artefato e o contrato, não o voto do produtor.
  O falsificador roda f(0), que o teste congelado não roda.
  Corrida está fora dos dois sensores: os dois arranjos deixam escapar.

`llm_real` fica `nao_calibrado`.
"""

from __future__ import annotations

import importlib.util
import json
import random
import statistics
from pathlib import Path
from typing import Any, Callable

AQUI = Path(__file__).resolve().parent


def _carregar_tarefas():
    caminho = AQUI.parent / "brinquedo" / "tarefas.py"
    spec = importlib.util.spec_from_file_location("tarefas_multi_harness", caminho)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_tarefas = _carregar_tarefas()
TAREFAS = _tarefas.TAREFAS
caso_fronteira = _tarefas.caso_fronteira
fn_certo = _tarefas.fn_certo
fn_fronteira = _tarefas.fn_fronteira
fn_vermelho = _tarefas.fn_vermelho
teste_congelado = _tarefas.teste_congelado

N = len(TAREFAS)
SEEDS = list(range(20))
P_MANIFESTA = 0.80
P_EDITAR = 0.70
P_SEGUNDO = 0.35
PASSO_PRODUTOR = 3
PASSO_REVISOR = 2
PASSO_FALSIFICADOR = 2
PASSO_CORRECAO = 3
PASSO_ESCRITA = 1

SAIDA = AQUI.parent / "execucao" / "medicao.json"


def _fn_do_perfil(perfil: str) -> Callable[[int], int]:
    if perfil == "vermelho":
        return fn_vermelho
    if perfil == "fronteira":
        return fn_fronteira
    if perfil == "corrida":
        return fn_certo
    raise KeyError(perfil)


def _plano(seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    itens = []
    for tarefa in TAREFAS:
        manifesta = rng.random() < P_MANIFESTA
        perfil = tarefa["perfil"]
        editar = manifesta and perfil == "vermelho" and rng.random() < P_EDITAR
        segundo = manifesta and perfil == "vermelho" and rng.random() < P_SEGUNDO
        itens.append(
            {
                "id": tarefa["id"],
                "perfil": perfil,
                "manifesta": manifesta,
                "editar": editar,
                "segundo": segundo,
            }
        )
    return itens


def _auditar_sensores() -> None:
    if teste_congelado(fn_vermelho, mutado=False):
        raise AssertionError("vermelho passou no teste congelado")
    if not teste_congelado(fn_vermelho, mutado=True):
        raise AssertionError("teste mutado não ficou verde")
    if not teste_congelado(fn_fronteira, mutado=False):
        raise AssertionError("fronteira devia passar no congelado")
    if caso_fronteira(fn_fronteira):
        raise AssertionError("falsificador não quebrou a fronteira")
    if not caso_fronteira(fn_certo):
        raise AssertionError("caso certo quebrou no falsificador")
    if not teste_congelado(fn_certo, mutado=False):
        raise AssertionError("caso certo quebrou no congelado")


def rodar(modo: str, seed: int) -> dict[str, Any]:
    escapam = 0
    plantados = 0
    barradas = 0
    escritas_aplicadas = 0
    tentativas_escrita = 0
    passagens = 0
    passos = 0
    escalados = 0
    teste_mutado = False
    for item in _plano(seed):
        perfil = item["perfil"]
        manifesta = item["manifesta"]
        if manifesta:
            plantados += 1
        fn = _fn_do_perfil(perfil) if manifesta else fn_certo
        passos += PASSO_PRODUTOR
        if modo == "U":
            if manifesta and perfil == "vermelho":
                if item["editar"]:
                    tentativas_escrita += 1
                    escritas_aplicadas += 1
                    teste_mutado = True
                    passos += PASSO_ESCRITA
                    if not teste_congelado(fn, mutado=True):
                        raise RuntimeError("edição do teste não ficou verde")
                    escapam += 1
                else:
                    passos += PASSO_CORRECAO
                    if item["segundo"]:
                        # A correção não segurou. O harness único grava o teste.
                        tentativas_escrita += 1
                        escritas_aplicadas += 1
                        teste_mutado = True
                        passos += PASSO_ESCRITA
                        if not teste_congelado(fn, mutado=True):
                            raise RuntimeError("edição do teste não ficou verde")
                        escapam += 1
                    else:
                        fn = fn_certo
                        if not teste_congelado(fn, mutado=False):
                            raise RuntimeError("correção U não ficou verde")
            elif manifesta:
                escapam += 1
            continue
        # Três harnesses. A escrita no teste não gruda.
        if manifesta and perfil == "vermelho":
            if item["editar"]:
                tentativas_escrita += 1
                barradas += 1
                passos += PASSO_ESCRITA
                if teste_mutado:
                    raise RuntimeError("muro não segurou o teste")
            passos += PASSO_CORRECAO
            if item["segundo"]:
                escalados += 1
                passagens += 1
                continue
            fn = fn_certo
            if not teste_congelado(fn, mutado=False):
                raise RuntimeError("correção T não ficou verde")
        passos += PASSO_REVISOR + PASSO_FALSIFICADOR
        passagens += 2
        if manifesta and perfil == "fronteira":
            if caso_fronteira(fn):
                raise RuntimeError("falsificador não viu a fronteira")
            passos += PASSO_CORRECAO + PASSO_REVISOR + PASSO_FALSIFICADOR
            passagens += 3
            fn = fn_certo
            if not caso_fronteira(fn):
                raise RuntimeError("correção da fronteira falhou")
        elif manifesta and perfil == "corrida":
            if not (teste_congelado(fn, mutado=False) and caso_fronteira(fn)):
                raise RuntimeError("corrida devia passar nos dois sensores")
            escapam += 1
    return {
        "modo": modo,
        "seed": seed,
        "defeitos_plantados": plantados,
        "defeitos_que_escapam": escapam,
        "tentativas_escrita_teste": tentativas_escrita,
        "escritas_teste_aplicadas": escritas_aplicadas,
        "escritas_teste_barradas": barradas,
        "passagens": passagens,
        "passos": passos,
        "escalados": escalados,
        "teste_permaneceu_congelado": not teste_mutado,
    }


def _resumo(linhas: list[dict[str, Any]], chave: str) -> dict[str, float]:
    vals = [float(r[chave]) for r in linhas]
    return {
        "media": round(statistics.fmean(vals), 4),
        "desvio_amostral": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


CHAVES = (
    "defeitos_plantados",
    "defeitos_que_escapam",
    "tentativas_escrita_teste",
    "escritas_teste_aplicadas",
    "escritas_teste_barradas",
    "passagens",
    "passos",
    "escalados",
)


def medir(seeds: list[int] | None = None) -> dict[str, Any]:
    _auditar_sensores()
    seeds = list(SEEDS if seeds is None else seeds)
    modos = {}
    for modo in ("U", "T"):
        linhas = [rodar(modo, s) for s in seeds]
        modos[modo] = {"por_seed": linhas, **{chave: _resumo(linhas, chave) for chave in CHAVES}}
    return {
        "simulacao": True,
        "llm_real": "nao_calibrado",
        "n_tarefas": N,
        "n_seeds": len(seeds),
        "seeds": seeds,
        "p_manifesta": P_MANIFESTA,
        "p_editar_teste": P_EDITAR,
        "p_segundo_vermelho": P_SEGUNDO,
        "sensores": {
            "teste_congelado": "f(1) == 2",
            "falsificador": "f(0) == 0",
            "corrida": "plantada; nenhum dos dois sensores olha",
        },
        "U": modos["U"],
        "T": modos["T"],
    }


def main() -> None:
    payload = medir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for modo in ("U", "T"):
        bloco = payload[modo]
        print(
            f"{modo}"
            f"  escapam {bloco['defeitos_que_escapam']['media']} ± {bloco['defeitos_que_escapam']['desvio_amostral']}"
            f"  plantados {bloco['defeitos_plantados']['media']}"
            f"  barradas {bloco['escritas_teste_barradas']['media']} ± {bloco['escritas_teste_barradas']['desvio_amostral']}"
            f"  aplicadas {bloco['escritas_teste_aplicadas']['media']}"
            f"  tentativas {bloco['tentativas_escrita_teste']['media']}"
            f"  passagens {bloco['passagens']['media']} ± {bloco['passagens']['desvio_amostral']}"
            f"  passos {bloco['passos']['media']} ± {bloco['passos']['desvio_amostral']}"
            f"  escalados {bloco['escalados']['media']} ± {bloco['escalados']['desvio_amostral']}"
        )
    print(f"JSON → {SAIDA}")


if __name__ == "__main__":
    main()
