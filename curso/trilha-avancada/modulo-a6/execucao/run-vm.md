# Corrida real — A6

`utc 2026-11-12T14:55:25Z`  `segundos_total=7.391`

```
=== A6.1 alvos LoRA (params) ===
  qv           n_treino=460,800  frac=0.0034
  attn         n_treino=921,600  frac=0.0068
  mlp          n_treino=1,520,640  frac=0.0112
  all_linear   n_treino=2,442,240  frac=0.0178
=== A6.2 merge π_SFT vs adapter ===
  status=ok delta_max=4.673e-05 passou=True
=== A6.3 multi-adapter Amplitude + soma ===
  status=ok json_ok=True soma_4=True
=== A6.4 GGUF / Ollama ===
  nao_calibrado llama_cpp=False ollama=None
```

pytest A6: 3 passed (1 `modelo`).
