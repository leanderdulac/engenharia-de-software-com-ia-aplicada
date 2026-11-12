# Corrida real — A1 (VM de autoria)

Nada inventado. Tokenizer SmolLM2 + Qwen2.5-0.5B; pesos só do 135M.

## Hardware e software

```
utc 2026-11-12T14:38:51Z
uname Linux 6.12.113+ x86_64
cpu Intel(R) Xeon(R) Processor
nproc 4
MemTotal:       16387328 kB
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
pytest 9.2.0
```

JSON: [`ca1-autoria.json`](./ca1-autoria.json). `epoch_unix=1794494331`.

## `python modulo-a1/lab/lab_a1.py`

`segundos_total=3.146`  `exit=0`

```
=== Lab A1.1 — tokenização PT vs EN ===
  sinistro SmolLM2  PT=21 tok  EN=15 tok  razão PT/EN=1.400
  quebra 'Segurado': ['Seg', 'ur', 'ado']
=== Lab A1.2 — softmax / greedy / warpers / entropia ===
  greedy ids iguais ao generate: True  texto='4\n\nA = 1\n'
  Δ T=0.000e+00  Δ top-k=0.000e+00  Δ top-p=0.000e+00
  entropia T=0,1 → T=2: [0.001, 0.678, 2.058, 6.068, 9.098]
```

## pytest

`python -m pytest modulo-a1/testes -q` → 11 passed (8 sem modelo + 3 com SmolLM2-135M).

## Limitações

- CPU only; T4 / Prompt API / custo/1k não calibrados.
- Pesos do Qwen2.5-0.5B **não** foram baixados (só tokenizer).
- A0 esqueleto: sem `bancada.json`.
- Greedy em 8 tokens; não é avaliação de degeneração de Holtzman em texto longo.
