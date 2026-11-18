# A6 — LoRA na prática de produção

**Status:** esqueleto (não publicado). **Carga prevista:** 5 h. **Pré-requisito previsto:** A5.

O M09 já faz LoRA/QLoRA e trade-off de rank. Falta ablação de *alvos* (atenção vs FFN vs all-linear), merge sem perda, dois adapters num base, GGUF/Ollama. Leitura extra já vendored: [`referencia/llm-course/modulo-06-lora/`](../../../referencia/llm-course/modulo-06-lora/) (Apache-2.0).

**CA6:** tabela parâmetros×métrica×tempo; Δ de logits no merge < 1e-3; cada adapter vence no próprio retido; GGUF responde no Ollama com queda declarada.
