# A0 — Bancada: ambiente, medição e orçamento

Trilha avançada, **opcional**. Guia: [`README.md`](./README.md). Checkpoint: [`checkpoint-ca0.md`](./checkpoint-ca0.md). Sem gabarito nesta aula.

Antes de treinar LoRA (A5) ou destilar (A10) você precisa de uma **bancada**: versões, semente, latência, memória. O M09 já ensina o pôster de GPU; aqui você *mede* no processo. Ao final:

1. listar as versões que realmente importam (`torch`, `transformers`, `peft`, `trl`);
2. gerar 20 respostas e ler p50, p95, tokens/s e pico de RSS no JSON;
3. repetir a corrida e aceitar p50 em ±20%;
4. montar o envelope pesos+grad+Adam — e marcar T4 como não calibrado nesta CPU.

Nada disto entra nas 240 h. Números **não** se copiam da aula: saem do seu `ca0.json`.

---

## 0. Honestidade

| O plano pedia | O que este módulo faz |
| --- | --- |
| Instruct ~0,5B | SmolLM2-135M (Apache-2.0, cache da trilha). Qwen2.5-0.5B = `nao_baixado` (`TRILHA_A0_MODELO`) |
| Trackio / TensorBoard | JSON. Trackio `nao_instalado` |
| T4 / Kaggle 2×T4 / Mac | CPU; T4 = `nao_calibrado` |
| bitsandbytes | ausente nesta VM (`null`) |

O pôster [`gpu-cuda-anatomia-poster.html`](../../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft/gpu-cuda-anatomia-poster.html) do M09 **não** é copiado. Leia-o; esta aula só usa a conta de envelope.

---

## 1. Por que pinar versão

`transformers` e `trl` mudam API. Um DPOConfig de 2025 quebra em 2026. A bancada grava o que *rodou*: nesta VM `torch 2.15.0+cpu`, `transformers 5.22.2`, `peft 0.21.2`, `trl 1.17.1`. Sem isso, o A8/A9 vira “na minha máquina funciona”.

Semente: `torch.manual_seed` + `do_sample=False`. Greedy ainda varia milissegundos (CPU). Por isso CA0 pede ±20% no p50, não igualdade bit a bit.

---

## 2. O que medir

Para 20 prompts, 8 tokens novos, seed 0, nesta CPU:

| Métrica | corrida 1 | corrida 2 |
| --- | ---: | ---: |
| p50 (s/prompt) | 0,172 | 0,163 |
| p95 | 0,186 | 0,190 |
| tokens/s | 46,0 | 48,7 |
| pegada | 538 MB | 538 MB |
| RSS pico | 993 MB | 993 MB |

`p50_repetivel_20pct = true`. Pegada ≈ pesos fp32 (134 515 008 × 4 B = 538 MB). RSS é o processo (tokenizer, Python, cache).

---

## 3. Envelope de memória (treino)

Sem ativações: `pesos + grad + 2×Adam`. fp32:

```text
538 + 538 + 1076 = 2152 MB
```

Ativações e KV (A11) entram depois. T4 de 16 GB *cabe* neste envelope — **não medimos** T4 aqui.

---

## 4. O que fazer agora

1. `python modulo-a0/lab/lab_a0.py`
2. CA0 com o JSON **seu**. Se p50 sair de ±20%, declare hardware, não invente 0,172.
3. Opcional: [`tutor/mapa-a0.md`](./tutor/mapa-a0.md).
