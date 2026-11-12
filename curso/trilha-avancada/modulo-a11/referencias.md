# Referências primárias — A11

Conferidas na API do arXiv / card Hugging Face em 12/11/2026. Citação acadêmica; o texto da aula é original.

## Papers

| Paper | Primeiro autor | Ano | arXiv | O que o A11 usa |
| --- | --- | --- | --- | --- |
| *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer* | Shazeer | 2017 | [1701.06538](https://arxiv.org/abs/1701.06538) | camada MoE, `y = Σ G_i E_i`, gating esparso |
| *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity* | Fedus | 2021 | [2101.03961](https://arxiv.org/abs/2101.03961) | *k*=1; aux loss `N · Σ f_i P_i` (Eq. 4 no HTML do arXiv); α ≈ 10⁻² |
| *Mixtral of Experts* | Jiang | 2024 | [2401.04088](https://arxiv.org/abs/2401.04088) | 8 experts, top-2, decoder-only; Apache-2.0; 47B totais / 13B ativos |
| *OLMoE: Open Mixture-of-Experts Language Models* | Muennighoff | 2024 | [2409.02060](https://arxiv.org/abs/2409.02060) | 64 experts, top-8, 7B/1B; especialização; Apache-2.0 nos pesos |
| *Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference* | Jacob | 2018 | [1712.05877](https://arxiv.org/abs/1712.05877) | QAT, quantização simulada, STE (round no forward, identidade no backward) |
| *Efficient Memory Management for Large Language Model Serving with PagedAttention* | Kwon | 2023 | [2309.06180](https://arxiv.org/abs/2309.06180) | KV cache paged, vLLM, continuous batching — **leitura**; não medido nesta CPU |

Não usamos GPTQ/AWQ como lab (GPU). NF4/QLoRA permanecem no M09.

## Modelos (lab)

| Id | Licença (card, nov/2026) | Notas |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | PTQ e KV; o mesmo do A2 |
| [`ibm-granite/granite-3.1-1b-a400m-instruct`](https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct) | Apache-2.0 | `granitemoe`; 32 experts / top-8; ~1,3B / ~400M ativos (tabela do card) |
| [`allenai/OLMoE-1B-7B-0924-Instruct`](https://huggingface.co/allenai/OLMoE-1B-7B-0924-Instruct) | Apache-2.0 | só `AutoConfig` nesta VM; pesos ~7B bf16 |

## Software

- PyTorch `torch.ao.quantization.quantize_dynamic` (INT8 CPU). Deprecated em favor do `torchao`; o lab documenta o aviso.
- Hugging Face `transformers` (`AutoConfig`, `output_router_logits`, `generate(use_cache=…)`). Versão de autoria: a do `ca11.json`.
- MiniDecoder / atenção do A2 (prova de cache). Não modifica arquivos do A2.

## Tronco (citação, sem cópia)

- M08: nota “MoE ≠ multiagente”; serving / Ollama.
- M09: LoRA `q_proj`/`v_proj`, QLoRA NF4, harness do decimal — **não** republicamos JSONL.
- A2: bloco denso, GQA, máscara causal.
