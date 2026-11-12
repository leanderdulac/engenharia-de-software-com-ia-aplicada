# A6 — LoRA na prática de produção

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca6.md`](./checkpoint-ca6.md). Sem gabarito nesta aula.

O M09 já escolhe rank. Aqui: *onde* o adapter entra, o merge que some com o LoRA na inferência, dois adapters no mesmo denso, e o que **não** rodamos (GGUF/Ollama). Ao final:

1. ler a tabela qv / attn / mlp / all-linear (params, não magia);
2. apontar Δ de logits no merge < 1e-3 no JSON;
3. dizer qual adapter vence no JSON e qual na soma;
4. marcar GGUF como `nao_calibrado`.

Nada disto entra nas 240 h. Números saem do seu `ca6.json`. Leitura extra Apache-2.0 (não copiada): [`referencia/llm-course/modulo-06-lora/`](../../../../referencia/llm-course/modulo-06-lora/).

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| Ablação completa no harness | só contagem de params + π_SFT já treinado |
| GGUF / Ollama | `nao_calibrado` |
| T4 | `nao_calibrado` |
| MiniGPT llm-course | apontado, **não copiado** |

---

## 1. Alvos

LoRA r=8 em mais módulos = mais params treináveis, não necessariamente melhor JSON. `qv` é o do A5. `mlp` mexe no FFN. `all_linear` é o teto barato neste 135M.

---

## 2. Merge

`merge_and_unload` soma BA no peso. Com dropout 0 e fp32, os logits do adapter e do denso mergeado coincidem até ruído (~1e-3). Se Δ explode, o merge não foi no dtype certo.

---

## 3. Multi-adapter

O mesmo SmolLM2 carrega `amplitude` (π_SFT) e `soma` (SFT curto em `2+2=`). `set_adapter` troca o par A,B. Misturar os dois na mesma forward sem `add`/`cat` não é MoE (A11).

---

## 4. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| params qv / attn / mlp / all | 460 800 / 921 600 / 1 520 640 / 2 442 240 |
| Δ merge | **4,67×10⁻⁵** (< 1e-3) |
| Amplitude no JSON | começa `{"segurado":"Eva Martins"...` |
| Soma no JSON | ecoa o user (não JSON) |
| `2+2=` | ambos emitem `4` (π_SFT já acertava) |
| GGUF | `nao_calibrado` (`llama_cpp` ausente) |

---

## 5. O que fazer agora

1. `python modulo-a6/lab/lab_a6.py`
2. CA6 com o JSON **seu**.
