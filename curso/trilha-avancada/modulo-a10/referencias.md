# Referências primárias — A10

Conferidas na API do arXiv / card Hugging Face em 12/11/2026.

## Papers

| Paper | Ano | arXiv | O que o A10 usa |
| --- | --- | --- | --- |
| *Distilling the Knowledge in a Neural Network* (Hinton, Vinyals, Dean) | 2015 | [1503.02531](https://arxiv.org/abs/1503.02531) | softmax / T, KL, T² |
| *Sequence-Level Knowledge Distillation* (Kim & Rush) | 2016 | [1606.07947](https://arxiv.org/abs/1606.07947) | CE na sequência gerada pelo professor |
| *DistilBERT* (Sanh et al.) | 2019 | [1910.01108](https://arxiv.org/abs/1910.01108) | KD em Transformer (citação; não reproduzido) |
| *On-Policy Distillation of Language Models* (Agarwal et al., GKD) | 2023 | [2306.13649](https://arxiv.org/abs/2306.13649) | extensão on-policy (aula) |

## Modelos (licença no card, nov/2026)

| Id | Licença | Papel |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-360M`](https://huggingface.co/HuggingFaceTB/SmolLM2-360M) | Apache-2.0 | professor |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | aluno |
| [`Qwen/Qwen2.5-0.5B`](https://huggingface.co/Qwen/Qwen2.5-0.5B) | Apache-2.0 | alternativa **não usada** (tokenizer ≠) |

`huggingface_hub.model_info(...).cardData["license"]` = `apache-2.0` nos três, 12/11/2026.
