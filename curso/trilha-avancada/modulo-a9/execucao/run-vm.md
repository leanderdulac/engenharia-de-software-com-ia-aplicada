# Corrida real — A9 (VM de autoria)

Nada inventado. SmolLM2-135M em cache. `GRPOTrainer.train()` rodou nesta CPU, **3 seeds**.

## Hardware e software

```
utc 2026-11-12T14:23:03Z
uname Linux 6.12.113+ x86_64
cpu Intel(R) Xeon(R) Processor
nproc 4
MemTotal:       16387328 kB
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
trl 1.17.1
peft 0.21.2
datasets 5.2.0
pytest 9.2.0
```

JSON: [`ca9-autoria.json`](./ca9-autoria.json). `epoch_unix=1794493383`.

## `WANDB_DISABLED=true TRILHA_A9_PASSOS=16 TRILHA_A9_G=4 TRILHA_A9_SEEDS=0,1,2 python modulo-a9/lab/lab_a9.py`

`segundos_total=68.589`  `exit=0`

```
=== A9.1 REINFORCE brinquedo ===
  com baseline fim=1.000 p*=0.972 sem fim=1.000 p*=0.982
=== A9.2 reward hacking ===
  divergencias=2
=== A9.3 GRPOTrainer beta=0  G=4 passos=16 seeds=[0, 1, 2] n_eval=80 n_treino=24 ===
  eval_antes r=0.600 acertos=48/80 treino_antes=0.708
     seed 0 eval 0.600→0.738 delta=+0.138 zero_std=5/16
     seed 1 eval 0.600→0.725 delta=+0.125 zero_std=4/16
     seed 2 eval 0.600→0.738 delta=+0.138 zero_std=1/16
  resumo delta media=0.133 desvio=0.007 claro=True
=== A9.4 GRPO beta=0.04 ===
  beta_pos ok kl_max 0.0159 kl_n_nao_zero 15 hack_base 1.0
```

## pytest

`python -m pytest modulo-a9/testes -q` → 5 passed (inclui `modelo`).
