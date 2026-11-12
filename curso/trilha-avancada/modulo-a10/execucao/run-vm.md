# Corrida real — A10 (VM de autoria)

Nada inventado. SmolLM2-360M e 135M. Destilação **treinou** LoRA nesta CPU.

## Hardware e software

```
utc 2026-11-12T14:27:03Z
uname Linux 6.12.113+ x86_64
cpu Intel(R) Xeon(R) Processor
nproc 4
MemTotal:       16387328 kB
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
trl 1.17.1
peft 0.21.2
huggingface_hub license: apache-2.0 (360M, 135M, Qwen2.5-0.5B)
pytest 9.2.0
```

JSON: [`ca10-autoria.json`](./ca10-autoria.json). `epoch_unix=1794493623`.

## `python modulo-a10/lab/lab_a10.py`

`segundos_total=27.735`  `exit=0`

```
=== A10.1 professor HuggingFaceTB/SmolLM2-360M gera + filtro ===
  gerados=32 aceitos=32 taxa=1.000 mesmo_tok=True
  professor eval acc=0.917 p50=0.146s pegada=1447.3
=== A10.2 aluno original HuggingFaceTB/SmolLM2-135M ===
  aluno_base acc=0.600 p50=0.045s pegada=538.1
=== A10.3 destilação por resposta (CE, 8 passos, n=32) ===
  seq acc=0.650 loss_fim=0.7147
=== A10.4 destilação por logits (T=2, 8 passos) ===
  logits T=2 acc=0.383 kl_fim=1.3384
```

## pytest

`python -m pytest modulo-a10/testes -q` → 3 passed (inclui `modelo`).
