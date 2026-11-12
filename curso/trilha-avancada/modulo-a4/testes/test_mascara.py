"""Máscara −100, split e padding sem baixar pesos."""

from __future__ import annotations

from types import SimpleNamespace

from dialogos_amplitude import dialogos_eval, dialogos_treino, split_ok
from mascarar_sft import IGNORE, colar, tensorizar, tensorizar_turnos


class FakeTok:
    eos_token = "</s>"
    eos_token_id = 0
    pad_token_id = 0

    def __call__(self, text, add_special_tokens=False):
        if text.endswith(self.eos_token):
            body = text[: -len(self.eos_token)]
            ids = [min(ord(c), 200) + 1 for c in body] + [self.eos_token_id]
        else:
            ids = [min(ord(c), 200) + 1 for c in text]
        return SimpleNamespace(input_ids=ids)


def test_split_treino_eval_disjunto():
    assert split_ok()
    assert len(dialogos_treino()) >= 3
    assert len(dialogos_eval()) >= 1


def test_prompt_vira_menos_100_e_assistant_bate_ids():
    tok = FakeTok()
    r = tensorizar(tok, "oi", "JSON", system="sys")
    assert all(x == IGNORE for x in r["labels"][: r["n_prompt"]])
    assert r["labels"][r["n_prompt"] :] == r["input_ids"][r["n_prompt"] :]
    assert r["n_assistant"] > 0
    assert r["termina_eos"]


def test_system_aumenta_o_prefixo():
    tok = FakeTok()
    com = tensorizar(tok, "u", "a", system="BLOCO SYSTEM LONGO")
    sem = tensorizar(tok, "u", "a", system=None)
    assert com["n_prompt"] > sem["n_prompt"]
    assert com["n_assistant"] == sem["n_assistant"]


def test_multi_turn_so_assistant_na_loss():
    tok = FakeTok()
    r = tensorizar_turnos(
        tok,
        [("user", "q1"), ("assistant", "r1"), ("user", "q2"), ("assistant", "r2")],
        system=None,
    )
    assert r["n_assistant"] < r["n_total"]
    assert all(x == IGNORE or x in r["input_ids"] for x in r["labels"])


def test_colar_pad_labels_menos_100():
    tok = FakeTok()
    a = tensorizar(tok, "curto", "x", system=None)
    b = tensorizar(tok, "um user bem mais longo que o outro", "yyyy", system=None)
    batch = colar([a, b], tok.pad_token_id)
    assert batch["L"] == b["n_total"]
    pad_labs = batch["labels"][0][a["n_total"] :]
    assert pad_labs and all(x == IGNORE for x in pad_labs)
    assert batch["attention_mask"][0][a["n_total"] :] == [0] * (batch["L"] - a["n_total"])
    trunc = colar([a, b], tok.pad_token_id, max_len=8)
    assert trunc["truncou"]
    assert trunc["L"] == 8
