# Corrida real — A9 (VM de autoria)

Nada inventado. SmolLM2-135M em cache. `GRPOTrainer.train()` rodou nesta CPU.

## Hardware e software

```
utc 2026-11-12T14:16:19Z
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

JSON: [`ca9-autoria.json`](./ca9-autoria.json). `epoch_unix=1794492979`.

## `WANDB_DISABLED=true TRILHA_A9_PASSOS=3 python modulo-a9/lab/lab_a9.py`

`segundos_total=10.742`  `exit=0`

```
=== A9.1 REINFORCE brinquedo ===
  com baseline fim=1.000 p*=0.972 sem fim=1.000 p*=0.982
=== A9.2 reward hacking (sinal, sem treino) ===
  divergencias=2 exata=[1.0, 0.0, 0.0, 0.0, 0.0] hack=[1.0, 1.0, 1.0, 0.0, 0.0]
=== A9.3 GRPOTrainer (beta=0, atualiza LoRA) ===
  eval antes r_media=0.500 acertos=2/4 treino_antes=0.875
  ... 3 passos, reward=[0.5, 0.5, 0.0], frac_reward_zero_std=[0,0,1] ...
  train_loss=0.0 rewards_log=[0.5, 0.5, 0.0] eval 0.500→0.750 treino_depois=0.875
=== A9.4 GRPO beta>0 (fumaça) + hack no mesmo gerado ===
  ... kl=0 ...
  beta_pos ok hack_base 1.0
```

Eval greedy: `7+1=` de `"10\n\nA."` (r=0) para `"8\n\nA. "` (r=1). Hack no base = 1,0 vs exata 0,5.

## pytest

`python -m pytest modulo-a9/testes -q` → `.....` (5 passed, inclui `modelo`).
