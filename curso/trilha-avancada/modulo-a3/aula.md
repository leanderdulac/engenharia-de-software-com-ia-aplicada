# A3 — Treino por dentro

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca3.md`](./checkpoint-ca3.md). Sem gabarito nesta aula.

O M09 *usa* Trainer. Aqui a conta abre: shift de labels, CE no próximo token, accumulation, clipping, envelope de memória. Ao final:

1. escrever `logits[:, :-1]` vs `ids[:, 1:]` e dizer por que o shift existe;
2. provar (com o JSON) que accumulation = batch maior com dropout off;
3. contrastar fp32/fp16/bf16 sem fingir que rodou T4;
4. ler loss caindo num mini-decoder *nosso*, não no MiniGPT do llm-course.

Nada disto entra nas 240 h. Números saem do seu `ca3.json`.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| MiniGPT + TinyStories | MiniDecoder original (~26k params) + corpus sintético (contador mod V). TinyStories `nao_baixado` |
| MiniGPT do `llm-course` | apontado, **não copiado** |
| T4 / bf16 | `nao_calibrado` |

O pôster GPU do M09 continua a leitura de envelope; não é republicado.

---

## 1. Shift e CE

O modelo em `t` não pode ver `t+1`. Com máscara causal (A2), `logits[t]` prediz `ids[t+1]`. A perda:

```text
CE( softmax(logits[:, :-1]),  ids[:, 1:] )
```

Sem o `:-1` / `1:`, você treina o modelo a copiar o token atual. Teacher forcing: mesmo se o passo 3 teria errado, o passo 4 vê o ouro. Geração (A1) é série; treino é paralelo.

---

## 2. LR, clipping, precisão

AdamW com `lr=0,05` neste brinquedo. Clip `1.0` evita explosão no começo (loss inicial ~32 neste vocab). fp32 nesta CPU. fp16/bf16: T4 `nao_calibrado`. Accumulation existe porque a VRAM não cabe o batch: soma-se o gradiente de `k` microbatches e divide por `k`.

---

## 3. O que o lab mediu

| Item | Medido |
| --- | --- |
| params (tie) | **26 240** |
| loss 40 passos | **31,88 → 0,0013** |
| acc próximo token | **1,000** (tarefa de contar) |
| Δ accum vs batch | **2,38×10⁻⁷** (< 1e-5) |
| envelope mini | 0,4 MB; RSS processo 320 MB (Python, não o 135M) |

A acurácia 1,0 **não** é SFT de Amplitude. É um autômato. O ponto é: shift + CE + Adam funcionam, e accumulation não mente.

---

## 4. O que fazer agora

1. `python modulo-a3/lab/lab_a3.py`
2. CA3 com o JSON **seu**.
3. Leitura extra opcional: [`referencia/llm-course/tools/minigpt.py`](../../../../referencia/llm-course/tools/minigpt.py) (Apache-2.0) — código de outro autor, não esta aula.
