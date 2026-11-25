# Corrida real — A4

`utc 2026-11-12T14:47:37Z`  `segundos_total=2.260`

```
=== A4.1 tokenizer + template declarado ===
  modelo=HuggingFaceTB/SmolLM2-135M chat_template=ausente
=== A4.2 treino/eval com e sem system ===
  treino+sys n_prompt=71.0 n_asst=31.75 frac_prompt=0.6907
  sem system n_prompt=38.0  Δprompt=33.00 tok
  eval n=2 split_ok=True todos_eos=True
=== A4.3 multi-turn (só assistant na loss) ===
  n_total=44 n_assistant=14 n_prompt=30
=== A4.4 padding / truncamento ===
  pad L=108 truncou=False | max_len=48 L=48 truncou=True asst 31.8→0.0
```

pytest A4: 6 passed.
