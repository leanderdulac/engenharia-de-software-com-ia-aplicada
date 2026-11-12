"""Resolver π_SFT e exact-match sem baixar pesos."""

from __future__ import annotations

import os

from pi_sft import manifesto, resolver
from sft_lora import exact_match


def test_exact_match_corta_linha():
    assert exact_match('{"a":1}\nprosa', '{"a":1}')
    assert not exact_match("nao", '{"a":1}')


def test_resolver_desliga_com_env(monkeypatch):
    monkeypatch.setenv("TRILHA_PI_SFT", "0")
    assert resolver() is None
    m = manifesto()
    assert m["ponto_partida"] == "smollm2_base"
    assert m["encontrado"] is False


def test_resolver_padrao_se_adapter_existir(monkeypatch):
    monkeypatch.delenv("TRILHA_PI_SFT", raising=False)
    p = resolver()
    m = manifesto()
    if p is None:
        assert m["ponto_partida"] == "smollm2_base"
    else:
        assert (p / "adapter_config.json").is_file()
        assert m["ponto_partida"] == "pi_sft"
    _ = os.environ
