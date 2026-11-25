#!/usr/bin/env python3
"""Simulação didática: loop tático versus regra e revisor de design.

Não é um LLM e não chama API. O mesmo plano (seed) roda em três modos:

- A: só o teste congelado. Atalho que fica verde entra.
- B: teste + regra mecânica (import cruzado, dependência sem ADR,
  orçamento de complexidade). Se a regra barra, o agente copia o corpo
  para dentro de api.py. A cópia passa no teste e a regra não a vê.
- C: B + revisor de design. O revisor lê o diff e o ADR. Não recebe o
  resultado do teste. Recusa cópia e parâmetro `legacy`. No export com
  `streaming`, não decide: escala para um humano e o débito não entra.

`llm_real` fica `nao_calibrado`.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import random
import statistics
from pathlib import Path
from typing import Any

AQUI = Path(__file__).resolve().parent


def _carregar_catalogo():
    caminho = AQUI.parent / "brinquedo" / "catalogo.py"
    spec = importlib.util.spec_from_file_location("catalogo_tatica", caminho)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_catalogo = _carregar_catalogo()
BASE = _catalogo.BASE
FEATURES = _catalogo.FEATURES
REGRA_MECANICA = _catalogo.REGRA_MECANICA

N = len(FEATURES)
SEEDS = list(range(20))
P_TENTAR = 0.75
P_BUG = 0.20
CUSTO_LIMPO = 4
CUSTO_ATALHO = 2
CUSTO_DISPARO = 1
PENALIDADE = 1
ORCAMENTO_CORPO = 4
SAIDA = AQUI.parent / "execucao" / "medicao.json"


def _custo(debito_antes: int, base: int) -> int:
    return base + PENALIDADE * debito_antes


def _executavel(src: str) -> str:
    linhas = []
    for linha in src.splitlines():
        if linha.startswith(("import ", "from ", "DEPENDENCIAS")):
            continue
        linhas.append(linha.replace("persistencia.", "").replace("dominio.", ""))
    return "\n".join(linhas) + "\n"


def _namespace(fontes: dict[str, str]) -> dict[str, Any]:
    ns: dict[str, Any] = {}
    for nome in ("persistencia.py", "dominio.py", "api.py"):
        exec(_executavel(fontes[nome]), ns)  # noqa: S102 — brinquedo local, sem entrada externa
    return ns


def _teste_verde(fontes: dict[str, str], feature_id: str) -> bool:
    try:
        ns = _namespace(fontes)
        if feature_id == "listar_sinistros":
            got = ns["listar_sinistros"]()
            return isinstance(got, list) and len(got) == 1 and got[0]["placa"] == "ABC1D23"
        if feature_id == "criar_sinistro":
            got = ns["criar_sinistro"]({"id": "s2", "placa": "XYZ9Z99"})
            return isinstance(got, dict) and got.get("ok") is True
        if feature_id == "anexar_nota":
            got = ns["anexar_nota"]("foto")
            return isinstance(got, dict) and got.get("ok") is True and got["registro"]["nota"] == "foto"
        if feature_id == "buscar_placa":
            return ns["buscar_placa"]() == "ABC1D23"
        if feature_id == "registrar_pagamento":
            got = ns["registrar_pagamento"](10)
            return got["valor"] == 10
        if feature_id == "listar_apolices":
            return ns["listar_apolices"]() == ["s1"]
        if feature_id == "consultar_segurado":
            got = ns["consultar_segurado"]("Ana")
            return got["nome"] == "Ana"
        if feature_id == "exportar_sinistros":
            got = ns["exportar_sinistros"]()
            return isinstance(got, list) and len(got) == 1
    except Exception:
        return False
    raise KeyError(feature_id)


def _funcoes_api(src: str) -> list[ast.FunctionDef]:
    arvore = ast.parse(src)
    return [no for no in arvore.body if isinstance(no, ast.FunctionDef)]


def _corpo(fn: ast.FunctionDef) -> str:
    return ast.unparse(ast.Module(body=fn.body, type_ignores=[])).strip()


def _regra_dispara(tipo: str, trecho: str) -> bool:
    """Regra mecânica. Não olha duplicação, `legacy` nem `streaming`."""
    if tipo not in REGRA_MECANICA:
        return False
    if tipo == "import_cruzado":
        return "import persistencia" in trecho
    if tipo == "dependencia_sem_adr":
        return 'DEPENDENCIAS = ["requests"]' in trecho
    if tipo == "complexidade":
        for fn in _funcoes_api(trecho):
            if len(fn.body) > ORCAMENTO_CORPO:
                return True
        return False
    return False


def revisor_design(tipo: str, trecho: str) -> str:
    """Lê o diff e o tipo diante do ADR. Não recebe resultado de teste.

    Devolve `ok`, `recusar` ou `escalar`.
    """
    if tipo == "debito_humano" and "streaming" in trecho:
        return "escalar"
    if any(_tem_lista_copiada(fn) or _corpo(fn) == CORPO_GRAVAR for fn in _funcoes_api(trecho)):
        return "recusar"
    if any("legacy" in arg.arg for fn in _funcoes_api(trecho) for arg in fn.args.args):
        return "recusar"
    return "ok"


CORPO_GRAVAR = "return {'ok': True, 'registro': registro}"


def _escrever(fontes: dict[str, str], trecho: str) -> dict[str, str]:
    novo = dict(fontes)
    novo["api.py"] = fontes["api.py"] + "\n" + trecho
    return novo


def _tem_lista_copiada(fn: ast.FunctionDef) -> bool:
    for no in ast.walk(fn):
        if not isinstance(no, ast.List) or len(no.elts) != 1:
            continue
        item = no.elts[0]
        if not isinstance(item, ast.Dict):
            continue
        chaves = [ast.unparse(k) for k in item.keys if k is not None]
        if "'id'" in chaves and "'placa'" in chaves:
            return True
    return False


def _evidencia(fontes: dict[str, str]) -> dict[str, int]:
    api = fontes["api.py"]
    funcoes = _funcoes_api(api)
    copias = sum(1 for fn in funcoes if _tem_lista_copiada(fn) or _corpo(fn) == CORPO_GRAVAR)
    return {
        "import_cruzado": sum(1 for fn in funcoes if "persistencia." in ast.unparse(fn)),
        "dependencia_sem_adr": 1 if 'DEPENDENCIAS = ["requests"]' in api else 0,
        "complexidade": sum(1 for fn in funcoes if len(fn.body) > ORCAMENTO_CORPO),
        "duplicacao": copias,
        "interface": sum(1 for fn in funcoes if any(arg.arg == "legacy" for arg in fn.args.args)),
        "debito_humano": sum(1 for fn in funcoes if any(arg.arg == "streaming" for arg in fn.args.args)),
    }


def _auditar_catalogo() -> None:
    for feat in FEATURES:
        for variante in ("limpo", "atalho", "evasao", "bug"):
            if variante not in feat:
                continue
            fontes = _escrever(BASE, feat[variante])
            verde = _teste_verde(fontes, feat["id"])
            if variante == "bug":
                if verde:
                    raise AssertionError(f"bug de {feat['id']} passou no teste")
            elif not verde:
                raise AssertionError(f"{variante} de {feat['id']} não passou no teste")
        if feat["tipo"] in REGRA_MECANICA:
            if not _regra_dispara(feat["tipo"], feat["atalho"]):
                raise AssertionError(f"regra não viu {feat['id']}")
            evasao = feat["evasao"]
            if _regra_dispara(feat["tipo"], evasao):
                raise AssertionError(f"regra viu a evasão de {feat['id']}")
            if revisor_design(feat["tipo"], evasao) != "recusar":
                raise AssertionError(f"revisor não recusou a evasão de {feat['id']}")
        elif feat["tipo"] == "debito_humano":
            if revisor_design(feat["tipo"], feat["atalho"]) != "escalar":
                raise AssertionError("revisor decidiu o débito humano")
        elif revisor_design(feat["tipo"], feat["atalho"]) != "recusar":
            raise AssertionError(f"revisor não recusou {feat['id']}")


def _contar(aceitos: list[str]) -> dict[str, int]:
    chaves = (
        "import_cruzado",
        "dependencia_sem_adr",
        "complexidade",
        "duplicacao",
        "interface",
        "debito_humano",
    )
    return {chave: sum(1 for item in aceitos if item == chave) for chave in chaves}


def rodar(modo: str, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    fontes = dict(BASE)
    aceitos: list[str] = []
    debito = 0
    passos = 0
    tentados = 0
    barrados_teste = 0
    disparos_regra = 0
    recusas_revisor = 0
    escalados = 0
    for feat in FEATURES:
        tenta = rng.random() < P_TENTAR
        bug = rng.random() < P_BUG if tenta else False
        if not tenta:
            passos += _custo(debito, CUSTO_LIMPO)
            fontes = _escrever(fontes, feat["limpo"])
            continue
        tentados += 1
        if bug:
            barrados_teste += 1
            passos += _custo(debito, CUSTO_ATALHO) + _custo(debito, CUSTO_LIMPO)
            fontes = _escrever(fontes, feat["limpo"])
            continue
        trecho = feat["atalho"]
        tipo_efetivo = feat["tipo"]
        if modo in {"B", "C"} and _regra_dispara(feat["tipo"], trecho):
            disparos_regra += 1
            passos += _custo(debito, CUSTO_DISPARO)
            trecho = feat["evasao"]
            tipo_efetivo = "duplicacao"
        if modo == "C":
            # O revisor recebe o trecho que seria gravado e o tipo da feature.
            # Não recebe o booleano do teste.
            julgamento = revisor_design(feat["tipo"], trecho)
            if julgamento == "escalar":
                escalados += 1
                recusas_revisor += 1
                passos += _custo(debito, CUSTO_LIMPO)
                fontes = _escrever(fontes, feat["limpo"])
                continue
            if julgamento == "recusar":
                recusas_revisor += 1
                passos += _custo(debito, CUSTO_LIMPO)
                fontes = _escrever(fontes, feat["limpo"])
                continue
        if not _teste_verde(_escrever(fontes, trecho), feat["id"]):
            raise RuntimeError(f"atalho verde ficou vermelho em {feat['id']} modo {modo}")
        aceitos.append(tipo_efetivo)
        debito += 1
        passos += _custo(debito - 1, CUSTO_ATALHO)
        fontes = _escrever(fontes, trecho)
    evidencia = _evidencia(fontes)
    contagem = _contar(aceitos)
    if evidencia != contagem:
        raise RuntimeError(f"evidência {evidencia} != aceite {contagem} modo {modo} seed {seed}")
    return {
        "modo": modo,
        "seed": seed,
        "entregues_teste_verde": N,
        "violacoes": len(aceitos),
        "duplicacao": contagem["duplicacao"],
        "custo_feature_seguinte": _custo(debito, CUSTO_LIMPO),
        "passos": passos,
        "atalhos_tentados": tentados,
        "atalhos_aceitos": len(aceitos),
        "barrados_pelo_teste": barrados_teste,
        "disparos_regra": disparos_regra,
        "recusas_revisor": recusas_revisor,
        "escalados": escalados,
        "por_tipo": contagem,
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
    "entregues_teste_verde",
    "violacoes",
    "duplicacao",
    "custo_feature_seguinte",
    "passos",
    "atalhos_tentados",
    "atalhos_aceitos",
    "barrados_pelo_teste",
    "disparos_regra",
    "recusas_revisor",
    "escalados",
)


def medir(seeds: list[int] | None = None) -> dict[str, Any]:
    _auditar_catalogo()
    seeds = list(SEEDS if seeds is None else seeds)
    modos = {}
    for modo in ("A", "B", "C"):
        linhas = [rodar(modo, s) for s in seeds]
        modos[modo] = {"por_seed": linhas, **{chave: _resumo(linhas, chave) for chave in CHAVES}}
    return {
        "simulacao": True,
        "llm_real": "nao_calibrado",
        "n_features": N,
        "n_seeds": len(seeds),
        "seeds": seeds,
        "p_tentar": P_TENTAR,
        "p_bug": P_BUG,
        "custo_limpo": CUSTO_LIMPO,
        "custo_atalho": CUSTO_ATALHO,
        "custo_disparo": CUSTO_DISPARO,
        "penalidade_por_debito": PENALIDADE,
        "orcamento_corpo": ORCAMENTO_CORPO,
        "custo_feature_seguinte_definicao": "CUSTO_LIMPO + PENALIDADE * violacoes acumuladas",
        "revisor_ve_testes": False,
        "A": modos["A"],
        "B": modos["B"],
        "C": modos["C"],
    }


def main() -> None:
    payload = medir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for modo in ("A", "B", "C"):
        bloco = payload[modo]
        print(
            f"{modo}"
            f"  entregues {bloco['entregues_teste_verde']['media']}"
            f"  violacoes {bloco['violacoes']['media']} ± {bloco['violacoes']['desvio_amostral']}"
            f"  dup {bloco['duplicacao']['media']} ± {bloco['duplicacao']['desvio_amostral']}"
            f"  seguinte {bloco['custo_feature_seguinte']['media']} ± {bloco['custo_feature_seguinte']['desvio_amostral']}"
            f"  passos {bloco['passos']['media']} ± {bloco['passos']['desvio_amostral']}"
            f"  tentados {bloco['atalhos_tentados']['media']}"
            f"  aceitos {bloco['atalhos_aceitos']['media']}"
            f"  teste {bloco['barrados_pelo_teste']['media']}"
            f"  regra {bloco['disparos_regra']['media']}"
            f"  revisor {bloco['recusas_revisor']['media']}"
            f"  escalados {bloco['escalados']['media']}"
        )
    print(f"JSON → {SAIDA}")


if __name__ == "__main__":
    main()
