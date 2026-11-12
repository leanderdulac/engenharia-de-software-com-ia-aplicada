import pytest

from merge_lora import delta_merge
from pi_sft import resolver

pytestmark = pytest.mark.modelo


def test_merge_pi_sft_delta_pequeno():
    assert resolver() is not None
    r = delta_merge()
    assert r["status"] == "ok"
    assert r["passou"], r["delta_max"]
    assert r["delta_max"] < 1e-3
