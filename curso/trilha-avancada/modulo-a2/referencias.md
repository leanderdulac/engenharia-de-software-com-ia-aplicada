# Referências primárias — A2

Conferidas na API do arXiv / DOI em 12/11/2026. Citação acadêmica; o texto da aula é original.

## Papers

| Paper | Primeiro autor | Ano | arXiv | O que o A2 usa |
| --- | --- | --- | --- | --- |
| *Attention Is All You Need* | Vaswani | 2017 | [1706.03762](https://arxiv.org/abs/1706.03762) | §3.2.1 produto interno escalado; §3.2.2 multi-head; §3.3 FFN; §3.5 senoides; Fig. 1 encoder-decoder |
| *Layer Normalization* | Ba | 2016 | [1607.06450](https://arxiv.org/abs/1607.06450) | norma por feature |
| *Root Mean Square Layer Normalization* | Zhang | 2019 | [1910.07467](https://arxiv.org/abs/1910.07467) | RMSNorm (Llama/Qwen/SmolLM2) |
| *RoFormer: Enhanced Transformer with Rotary Position Embedding* | Su | 2021 | [2104.09864](https://arxiv.org/abs/2104.09864) | RoPE |
| *GLU Variants Improve Transformer* | Shazeer | 2020 | [2002.05202](https://arxiv.org/abs/2002.05202) | SwiGLU |
| *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints* | Ainslie | 2023 | [2305.13245](https://arxiv.org/abs/2305.13245) | grouped-query attention |
| *Deep Residual Learning for Image Recognition* | He | 2016 | [1512.03385](https://arxiv.org/abs/1512.03385) | conexão residual (origem) |

## Modelos (lab)

| Id | Licença (card, nov/2026) | Notas |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | padrão CPU; `model_type=llama` |
| [`Qwen/Qwen2.5-0.5B`](https://huggingface.co/Qwen/Qwen2.5-0.5B) | Apache-2.0 | opcional (`TRILHA_A2_MODELO`) |

## Software

- PyTorch `torch.nn.functional.scaled_dot_product_attention` — referência numérica do A2.1.
- Hugging Face `transformers` (lab A2.2: `attn_implementation="eager"`, `output_attentions=True`, `output_hidden_states=True`). Versão de autoria: 5.22.2.
- MiniGPT de apoio (código Apache-2.0, **não** é esta aula): [`referencia/llm-course/tools/minigpt.py`](../../../referencia/llm-course/tools/minigpt.py). Autor: Luciano de Oliveira Nunes. Crédito: [`curso/ATRIBUICOES-llm-course.md`](../../ATRIBUICOES-llm-course.md).
- Módulo 02 do curso B (atenção), **não vendored** neste clone: [lucianoon/llm-course](https://github.com/lucianoon/llm-course).

## Tronco (citação, sem cópia)

- M01 aula, seção “LLM: amostragem, não oráculo” e lab `exemplo-04-webai02-temperature-and-topK`.
- M09 labs LoRA (`q_proj` / `v_proj` / `all-linear`).
