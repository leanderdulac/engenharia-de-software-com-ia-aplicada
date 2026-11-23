"""Doze funções de sinistro, originais, no espírito do caso Amplitude.

Não são o JSONL do M09. O par é (nome v1, nome v2 em snake_case).
A última, export, não tem decisão de streaming: o harness escala.
"""

from __future__ import annotations

FUNCOES: list[tuple[str, str]] = [
    ("getClaim", "get_claim"),
    ("listClaims", "list_claims"),
    ("postClaim", "post_claim"),
    ("getPolicy", "get_policy"),
    ("listPolicies", "list_policies"),
    ("postNote", "post_note"),
    ("getPlate", "get_plate"),
    ("listPlates", "list_plates"),
    ("postPayment", "post_payment"),
    ("getInsured", "get_insured"),
    ("listInsured", "list_insured"),
    ("exportClaims", "export_claims"),
]

EXPORT = 11
