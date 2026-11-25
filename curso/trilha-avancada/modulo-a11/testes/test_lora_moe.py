from __future__ import annotations

from lora_moe import LoRALinear, comparar_experts_vs_router, injetar, inspecionar_granite_alvos
from moe_brinquedo import CamadaMoE
import torch
from torch import nn


def test_lora_delta_inicial_nulo():
    torch.manual_seed(0)
    lin = nn.Linear(6, 5)
    x = torch.randn(3, 6)
    y0 = lin(x)
    wrap = LoRALinear(lin, r=2, alpha=4.0)
    y1 = wrap(x)
    assert torch.allclose(y0, y1, atol=1e-6)


def test_experts_tem_mais_params_lora_que_router():
    r = comparar_experts_vs_router(passos=12, semente=14)
    assert r["status"] == "ok"
    assert r["lora_experts_mais_params"]
    assert r["experts"]["n_treino_lora"] > r["router"]["n_treino_lora"]
    assert r["experts"]["mse_caiu"]
    assert r["router"]["n_treino_lora"] > 0


def test_granite_experts_sao_tensores_3d_nao_linear():
    g = inspecionar_granite_alvos()
    if g.get("status") != "ok_meta":
        return  # offline / transformers antigo: não inventar
    assert g["n_tensores_expert_3d"] == 48  # 24 camadas × gate_up + down
    assert g["num_local_experts"] == 32
    assert g["peft_linear_nao_casa_experts_3d"] is True
    assert g["n_treino_lora_experts"] > g["n_treino_lora_attn"] > 0
    assert g["treino"] == "nao_calibrado_cpu"


def test_injetar_congela_a_base():
    moe = CamadaMoE(d=8, n_experts=4, k=2, d_ff=16)
    info = injetar(moe, "experts")
    assert info["n_treino_lora"] > 0
    assert all(not p.requires_grad for p in moe.router.parameters())
    treino = [p for p in moe.parameters() if p.requires_grad]
    assert treino
    assert all(p.requires_grad for p in treino)
