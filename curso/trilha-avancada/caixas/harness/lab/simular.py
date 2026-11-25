#!/usr/bin/env python3
"""Simulação didática de harness. Não é um LLM e não chama API.

Dois modos, mesmas seeds, mesmo «agente» de brinquedo (memória curta,
compactação, chance de erro fixada pela seed):

- A: só chat. Relata sucesso pela própria impressão. Testes não rodam.
- B: contrato + PROGRESS.md + teste como portão + teto de tentativas
  + escrita bloqueada fora do escopo.

A migração de brinquedo são N funções v1→v2 (sinistro), não os 40
endpoints do artigo. Números do artigo não entram nesta conta.
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path
from typing import Any

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "brinquedo"))

from funcoes import EXPORT, FUNCOES  # noqa: E402

N = len(FUNCOES)
JANELA = 6
SEEDS = list(range(20))
P_ESCOPO = 0.22
P_FERRAMENTA_VAZIA = 0.18
ESQUEMA_CERTO = "snake"
ESQUEMA_ERRADO = "camel"

SAIDA = AQUI.parent / "execucao" / "medicao.json"


def _teste_verde(arquivo: tuple[str, str] | None) -> bool:
    return arquivo == ("rotas", ESQUEMA_CERTO)


def _escrever_a(
    rng: random.Random,
    arquivos: dict[int, tuple[str, str]],
    alvo: int,
    esquema: str,
) -> tuple[int, int]:
    """Uma tentativa no modo A. Devolve (violacao, desperdicada)."""
    if rng.random() < P_ESCOPO:
        arquivos[alvo] = ("db", esquema)
        return 1, 1
    antes = arquivos.get(alvo)
    arquivos[alvo] = ("rotas", esquema)
    desperdicada = 0
    if esquema != ESQUEMA_CERTO or (antes is not None and _teste_verde(antes)):
        desperdicada = 1
    return 0, desperdicada


def rodar_a(seed: int) -> dict[str, Any]:
    """Chat com shell. Uma compactação, esquece a regra, não roda teste, diz N/N.

    Passo 1: funções 0..JANELA-1 no esquema certo (cabe na janela).
    Passo 2: a janela compacta. A regra de nome e a lista do que já ficou
    pronto saem do contexto. O agente regrava duas funções já feitas com
    o esquema errado e segue o resto nesse esquema. A impressão conta
    tudo como pronto.
    """
    rng = random.Random(seed)
    arquivos: dict[int, tuple[str, str]] = {}
    violacoes = 0
    desperdicadas = 0
    tentativas = 0
    for alvo in range(JANELA):
        tentativas += 1
        v, d = _escrever_a(rng, arquivos, alvo, ESQUEMA_CERTO)
        violacoes += v
        desperdicadas += d
    # Compactação: o resumo não guarda o esquema nem os ids prontos.
    refeitos = rng.sample(range(JANELA), 2)
    for alvo in refeitos:
        tentativas += 1
        v, _ = _escrever_a(rng, arquivos, alvo, ESQUEMA_ERRADO)
        violacoes += v
        desperdicadas += 1
    for alvo in range(JANELA, N):
        tentativas += 1
        v, d = _escrever_a(rng, arquivos, alvo, ESQUEMA_ERRADO)
        violacoes += v
        desperdicadas += d
    concluidas = sum(1 for i in range(N) if _teste_verde(arquivos.get(i)))
    return {
        "modo": "A",
        "seed": seed,
        "relatado": N,
        "concluidas": concluidas,
        "violacoes_escopo_aplicadas": violacoes,
        "tentativas_desperdicadas": desperdicadas,
        "tentativas": tentativas,
        "escalados": 0,
        "testes_rodados": False,
        "compactacoes": 1,
        "refeitos_com_outro_esquema": refeitos,
        "refeitos_v1": [FUNCOES[i][0] for i in refeitos],
    }


def rodar_b(seed: int) -> dict[str, Any]:
    """Contrato, estado em arquivo, sensor, teto e muro. Relata o que o teste diz."""
    rng = random.Random(seed)
    arquivos: dict[int, tuple[str, str]] = {}
    progresso = {
        "done": [],
        "current": None,
        "decisions": [f"campos v2 em {ESQUEMA_CERTO}; códigos de erro v1 ficam"],
        "dead_ends": [],
        "blocked": [],
    }
    violacoes_tentadas = 0
    violacoes_aplicadas = 0
    desperdicadas = 0
    tentativas = 0
    for i in range(N):
        progresso["current"] = i
        if i == EXPORT:
            progresso["blocked"].append(
                {"id": i, "motivo": "export exige decisão de streaming; não inventada"}
            )
            progresso["dead_ends"].append("inventar streaming no export")
            continue
        erros: list[str] = []
        for _ in range(2):
            tentativas += 1
            if rng.random() < P_FERRAMENTA_VAZIA and not erros:
                erros.append("ferramenta_vazia")
                desperdicadas += 1
                continue
            if rng.random() < P_ESCOPO:
                violacoes_tentadas += 1
                # Muro: db/ não aceita escrita. A tentativa conta; o arquivo não muda.
                erros.append("muro_db")
                desperdicadas += 1
                if erros.count("muro_db") >= 2:
                    progresso["blocked"].append({"id": i, "motivo": "mesmo erro duas vezes: muro_db"})
                    progresso["dead_ends"].append(f"endpoint {i}: editar db/")
                    break
                continue
            # A decisão mora no PROGRESS, fora da janela. Não se perde na compactação.
            arquivos[i] = ("rotas", ESQUEMA_CERTO)
            if _teste_verde(arquivos[i]):
                progresso["done"].append(i)
                break
            erros.append("sensor_vermelho")
            desperdicadas += 1
        else:
            if i not in progresso["done"] and not any(
                b["id"] == i for b in progresso["blocked"]
            ):
                progresso["blocked"].append({"id": i, "motivo": "teto de tentativas"})
    concluidas = sum(1 for i in range(N) if _teste_verde(arquivos.get(i)))
    return {
        "modo": "B",
        "seed": seed,
        "relatado": concluidas,
        "concluidas": concluidas,
        "violacoes_escopo_tentadas": violacoes_tentadas,
        "violacoes_escopo_aplicadas": violacoes_aplicadas,
        "tentativas_desperdicadas": desperdicadas,
        "tentativas": tentativas,
        "escalados": len(progresso["blocked"]),
        "testes_rodados": True,
        "progresso_done": len(progresso["done"]),
    }


def _resumo(linhas: list[dict[str, Any]], chave: str) -> dict[str, float]:
    vals = [float(r[chave]) for r in linhas]
    return {
        "media": round(statistics.fmean(vals), 4),
        "desvio_amostral": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


def medir(seeds: list[int] | None = None) -> dict[str, Any]:
    seeds = list(SEEDS if seeds is None else seeds)
    a = [rodar_a(s) for s in seeds]
    b = [rodar_b(s) for s in seeds]
    return {
        "simulacao": True,
        "llm_real": "nao_calibrado",
        "artigo_40_endpoints": "ilustrativo_nao_medido",
        "n_funcoes": N,
        "janela_contexto": JANELA,
        "n_seeds": len(seeds),
        "seeds": seeds,
        "p_escopo": P_ESCOPO,
        "p_ferramenta_vazia": P_FERRAMENTA_VAZIA,
        "export_bloqueado": EXPORT,
        "A": {
            "por_seed": a,
            "relatado": _resumo(a, "relatado"),
            "concluidas": _resumo(a, "concluidas"),
            "violacoes_escopo_aplicadas": _resumo(a, "violacoes_escopo_aplicadas"),
            "tentativas_desperdicadas": _resumo(a, "tentativas_desperdicadas"),
        },
        "B": {
            "por_seed": b,
            "relatado": _resumo(b, "relatado"),
            "concluidas": _resumo(b, "concluidas"),
            "violacoes_escopo_aplicadas": _resumo(b, "violacoes_escopo_aplicadas"),
            "violacoes_escopo_tentadas": _resumo(b, "violacoes_escopo_tentadas"),
            "tentativas_desperdicadas": _resumo(b, "tentativas_desperdicadas"),
            "escalados": _resumo(b, "escalados"),
        },
    }


def main() -> None:
    payload = medir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    a, b = payload["A"], payload["B"]
    print(
        f"A relatado {a['relatado']['media']}  concluidas {a['concluidas']['media']}"
        f" ± {a['concluidas']['desvio_amostral']}"
        f"  escopo {a['violacoes_escopo_aplicadas']['media']}"
        f"  desperdicio {a['tentativas_desperdicadas']['media']}"
    )
    print(
        f"B relatado {b['relatado']['media']}  concluidas {b['concluidas']['media']}"
        f" ± {b['concluidas']['desvio_amostral']}"
        f"  escopo_aplicado {b['violacoes_escopo_aplicadas']['media']}"
        f"  escopo_tentado {b['violacoes_escopo_tentadas']['media']}"
        f"  desperdicio {b['tentativas_desperdicadas']['media']}"
        f"  escalados {b['escalados']['media']}"
    )
    print(f"JSON → {SAIDA}")


if __name__ == "__main__":
    main()
