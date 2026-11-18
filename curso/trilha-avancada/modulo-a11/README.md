# A11 — MoE, quantização e serving eficiente

**Status:** esqueleto (não publicado). **Carga prevista:** 9 h. **Pré-requisito previsto:** A2, A6.

**Próximo módulo a construir** depois deste PR (A2). Hoje o tronco cita MoE numa nota (“≠ multiagente”) e mede NF4 no QLoRA; faltam router, experts, aux loss, colapso, PTQ vs QAT, KV cache e continuous batching.

**Labs previstos (quando sair):**

- MoE de brinquedo em CPU, 8 experts, top-2, histograma com/sem aux loss (CA11.1).
- Inspeção de MoE real pequeno (Granite 1B-A400M; OLMoE em 4 bits na T4) (CA11.2).
- LoRA em atenção vs experts (opcional) (CA11.3).
- O SFT do A5 em fp16 / int8 / NF4 / GGUF; achar o formato em que o bug do decimal do M09 volta (CA11.4).
- QAT de brinquedo no MiniGPT (CA11.5).
- KV cache on/off; vLLM ou llama-server com concorrência (CA11.6).

Depende de A2 (bloco, FFN, normas) e, para LoRA em MoE, de A6. Sem A6 publicado, a inspeção (11.1–11.2, 11.4 conceitual) ainda pode ser escrita com o LoRA do M09 como ponte — decisão na hora de construir.

Hardware honesto: treinar MoE grande está fora; inspecionar e fazer o brinquedo não.
