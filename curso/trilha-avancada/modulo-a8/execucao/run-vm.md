# Corrida real — A8 (VM de autoria)

Nada abaixo foi inventado. Pesos do SmolLM2-135M já estavam no cache (A2/A11). Esta corrida é a **pós-correção**: fronteira BPE + split treino/eval.

## Hardware e software

```
utc 2026-11-12T14:08:39Z
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

JSON: [`ca8-autoria.json`](./ca8-autoria.json).

## `WANDB_DISABLED=true python modulo-a8/lab/lab_a8.py`

`segundos_total=23.857`  `exit=0`

```
=== A8.1 pares e comprimento ===
  n=14 treino=10 eval=4 disjuntos=True chosen_chars=60.2 rejected_chars=74.3 razao=1.23
=== A8.2 DPO LoRA (TRL) ===
  fronteira_ok=True falhas=0
  base treino preferencia_bruta=0.500 eval preferencia_bruta=0.500
... 8 passos DPO ...
{'eval_loss': '0.6598', ... 'eval_rewards/accuracies': '1', 'eval_rewards/margins': '0.06853', ...}
{'train_runtime': '4.821', ... 'train_loss': '0.6797', ...}
=== A8.2b logps / margem vs base (eval hold-out) ===
  train_loss=0.6797339096665382 aviso_prefixo={'ocorreu': False, 'n': 0, 'amostra': []} acc_treino=1.000 acc_eval=1.000 margem_eval=0.661
  perdas {'dpo_sigmoid': 0.6609, 'ipo': 19.0631, 'simpo': 0.4145, 'orpo': 1.5761, 'kto': 0.4917}
=== A8.4 familia TRL ...
  ipo ok kto ok orpo ok simpo ok

JSON → modulo-a8/saidas/ca8.json  (23.857 s)
```

**Aviso TRL de prefixo:** 0 ocorrências no stderr (`grep -c "not a prefix"` → 0) e `aviso_prefixo_trl.ocorreu=false` no DPO, KTO, ORPO e SimPO.

## Números

| Item | Medido |
| --- | ---: |
| split | 10 treino / 4 eval, prompts disjuntos |
| fronteira | ok, 0 falhas |
| DPO `train_loss` | 0,679734 |
| TRL eval acc / margin (hold-out) | 1,0 / 0,06853 |
| acc implícita treino / eval vs base | 1,0 / 1,0 |
| margem log-ratio treino / eval | 1,110 / 0,661 |
| `preferencia_bruta` eval | 0,500 |
| perdas DPO/IPO/SimPO/ORPO/KTO | 0,661 / 19,063 / 0,414 / 1,576 / 0,492 |
| IPO/KTO/ORPO/SimPO `train_loss` fumaça | 25 / 0,499 / 2,917 / 2,297 |

## `python -m pytest modulo-a8/testes -q`

`exit=0`  `........` (8 testes, inclui `modelo`).
