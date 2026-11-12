# Corrida real — A8 (VM de autoria)

Nada abaixo foi inventado. Pesos do SmolLM2-135M já estavam no cache (A2/A11). A parede do lab **não** inclui o download inicial.

## Hardware e software

```
utc 2026-11-12T14:02:54Z
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

JSON gerado: [`ca8-autoria.json`](./ca8-autoria.json) (cópia de `saidas/ca8.json` desta corrida).

## `WANDB_DISABLED=true python modulo-a8/lab/lab_a8.py`

`segundos_total=30.536`  `exit=0`

```
=== A8.1 pares e comprimento ===
  n=12 chosen_chars=52.9 rejected_chars=69.8 razao=1.32
=== A8.2 DPO LoRA (TRL) ===
  base preferencia_bruta=0.500 (logp_chosen > logp_rejected no base)
... (8 passos DPO; dicts no JSON) ...
{'eval_loss': '0.659', ... 'eval_rewards/accuracies': '0.9167', 'eval_rewards/margins': '0.07122', ...}
{'train_runtime': '6.078', ... 'train_loss': '0.6899', ...}
=== A8.2b logps / margem vs base ===
  train_loss=0.689865954220295 acc_log=[0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0] acc_depois=0.917 margem=0.704
  perdas {'dpo_sigmoid': 0.6594, 'ipo': 19.1219, 'simpo': 0.8347, 'orpo': 3.1007, 'kto': 0.4912}
=== A8.4 familia TRL (IPO/KTO estaveis; ORPO/SimPO experimental) ===
{'loss': '25', ...}   # IPO 1 passo
{'train_loss': '25', ...}
... KTO 2 passos train_loss=0.4994 ...
... ORPO 1 passo train_loss=5.736 ...
... SimPO/CPO 1 passo train_loss=5.75 ...
  ipo ok kto ok orpo ok simpo ok

JSON → modulo-a8/saidas/ca8.json  (30.536 s)
```

Stdout completa desta corrida (dicts por passo) está no log da sessão; métricas canônicas = o JSON.

Aviso do TRL 1.17.1 (stderr, uma vez por trainer): *The tokenized prompt is not a prefix of the tokenized prompt+completion* — merge em `'":'`. Limitação real; não foi mascarada.

## Números que o gabarito usa

| Item | Medido |
| --- | ---: |
| chosen / rejected chars | 52,92 / 69,75 (razão 1,32) |
| DPO `train_loss` (8 passos, β=0,1) | 0,689866 |
| `eval_rewards/accuracies` | 0,916667 |
| `eval_rewards/margins` | 0,071216 |
| `preferencia_bruta` base → depois | 0,500 → 0,500 |
| margem log-ratio vs base | 0,704376 |
| perdas no mesmo lote (DPO/IPO/SimPO/ORPO/KTO) | 0,6594 / 19,1219 / 0,8347 / 3,1007 / 0,4912 |
| `dpo_vs_beta` 0,1 / 0,5 / 1,0 | 0,6594 / 0,5521 / 0,4680 |
| IPO fumaça `train_loss` (1 passo) | 25,0 |
| KTO `train_loss` (2 passos) | 0,499373 |
| ORPO / SimPO `train_loss` (1 passo) | 5,736 / 5,75 |
| T4 | `nao_calibrado` |

## `python -m pytest modulo-a8/testes -q --tb=short`

`exit=0`

```
.......                                                                  [100%]
```

Sete testes (6 sem modelo + 1 `modelo` com SmolLM2). `pytest -q -m "not modelo"` na pasta da trilha: 32 passed (A2+A11+A8).
