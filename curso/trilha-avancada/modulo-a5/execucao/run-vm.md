# Corrida real — A5

`utc 2026-11-12T14:52:57Z`  `segundos_total=24.607`

```
=== A5.0 probes no base (antes do SFT) ===
  base '2+2=' → '10.\n\nThe number of ways to arrange '
  base 'The capital of France is' → ' the capital of the country.\n\nThe capital of France'
=== A5.1 SFT assistant-only (π_SFT) ===
  loss 1.3377 → 0.0458 fracao_treino=0.0034
=== A5.2 eval Amplitude (treino vs hold-out) ===
  treino acc=1.000  eval acc=0.500
=== A5.3 probes gerais (esquecimento, sem GSM8K/Dolly) ===
  '2+2=' → '4\n\n(a) 4\n\n(b'
  'The capital of France is' → ' the city of Paris. Paris is the capital of France and'
=== A5.4 SFT prompt+resposta (mesmo n passos, não salva) ===
  full loss 3.3354 → 3.4399 eval acc=0.000
```

pytest A5: 4 passed. Adapter ~1,8 MB em `execucao/pi_sft/`.
