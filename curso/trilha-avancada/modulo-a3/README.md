# A3 — Treino por dentro

**Status:** esqueleto (não publicado). **Carga prevista:** 6 h. **Pré-requisito previsto:** A2.

Fecha o que o M09 *usa* nos notebooks sem abrir: deslocamento de labels, cross-entropy no próximo token, LR e schedule, accumulation, clipping, fp32/fp16/bf16, orçamento de memória (pesos + gradientes + Adam + ativações).

**Labs previstos:** MiniGPT de poucos milhões no TinyStories (CA3.1); prova de que accumulation equivale a batch maior com dropout off (CA3.2); planilha de memória vs pico medido (CA3.3). Reusa o pôster `gpu-cuda-anatomia-poster.html` do M09 como leitura, sem duplicá-lo.
