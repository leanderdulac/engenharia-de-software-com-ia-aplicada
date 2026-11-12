# A0 — Bancada: ambiente, medição e orçamento de GPU

**Status:** esqueleto (não publicado). **Carga prevista:** 2 h. **Pré-requisito:** M09 com C09.3 e C09.4.

Primeiro módulo da trilha quando a sequência pedagógica estiver completa. Objetivo: escolher CPU / Colab T4 / Kaggle 2×T4 / Mac, fixar versões (`transformers`, `peft`, `trl`, `bitsandbytes`, `accelerate`), medir memória como o pôster do M09 já ensina, registrar corrida (Trackio ou TensorBoard).

**Lab previsto A0.1:** carregar um instruct de ~0,5B, gerar 20 respostas, gravar latência p50/p95, tokens/s e pico de memória em `bancada.json`. **CA0:** o arquivo tem ambiente, versões, GPU, as três métricas e a semente; repetir a corrida mantém p50 em ±20%.

Não faz parte das 240 h. Hardware: o curso não fornece GPU.
