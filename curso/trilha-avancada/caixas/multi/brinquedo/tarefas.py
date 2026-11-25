"""Seis mudanças de sinistro e os sensores de cada harness.

O teste congelado só chama f(1). O falsificador chama f(0).
A corrida não está em nenhum dos dois: o laboratório planta o defeito
e os sensores não o veem. Isso é limite do contrato, não um ajuste de número.
"""

from __future__ import annotations

TAREFAS: list[dict[str, str]] = [
    {"id": "corrigir_placa", "perfil": "vermelho"},
    {"id": "fechar_sinistro", "perfil": "fronteira"},
    {"id": "aplicar_franquia", "perfil": "vermelho"},
    {"id": "reabrir", "perfil": "corrida"},
    {"id": "calcular_reserva", "perfil": "fronteira"},
    {"id": "notificar_segurado", "perfil": "vermelho"},
]


def fn_vermelho(n: int) -> int:
    return 0


def fn_fronteira(n: int) -> int:
    return n + 1


def fn_certo(n: int) -> int:
    return 0 if n == 0 else n + 1


def teste_congelado(fn, mutado: bool) -> bool:
    if mutado:
        return True
    return fn(1) == 2


def caso_fronteira(fn) -> bool:
    return fn(0) == 0
