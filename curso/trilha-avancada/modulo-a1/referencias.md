# Referências primárias — A1

Conferidas na API do arXiv / card Hugging Face em 12/11/2026. Citação acadêmica; o texto da aula é original.

## Papers

| Paper | Primeiro autor | Ano | arXiv / fonte | O que o A1 usa |
| --- | --- | --- | --- | --- |
| *Neural Machine Translation of Rare Words with Subword Units* | Sennrich | 2016 | [1508.07909](https://arxiv.org/abs/1508.07909) | BPE como segmentação; vocabulário aberto via subwords |
| *A New Algorithm for Data Compression* | Gage | 1994 | C Users J. 2(2) | BPE original (compressão); Sennrich adapta |
| *The Curious Case of Neural Text Degeneration* | Holtzman | 2019 | [1904.09751](https://arxiv.org/abs/1904.09751) | núcleo / top-p; degeneração de maximização |
| *Hierarchical Neural Story Generation* | Fan | 2018 | [1805.04833](https://arxiv.org/abs/1805.04833) | top-k sampling (citado por Holtzman) |
| *Language Models are Unsupervised Multitask Learners* | Radford | 2019 | OpenAI | GPT-2 decoder-only gerativo (aula; pesos **não** baixados) |
| *Language Models are Few-Shot Learners* | Brown | 2020 | [2005.14165](https://arxiv.org/abs/2005.14165) | foundation / few-shot em escala (aula; pesos **não** baixados) |

Holtzman 1904.09751: título *The Curious Case of Neural Text Degeneration* (v2, 14 fev 2020). Sennrich 1508.07909: *Neural Machine Translation of Rare Words with Subword Units*.

## Modelos (lab)

| Id | Licença (card, nov/2026) | Papel |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | tokenizer + pesos (A1.2) |
| [`Qwen/Qwen2.5-0.5B`](https://huggingface.co/Qwen/Qwen2.5-0.5B) | Apache-2.0 | **só tokenizer** (A1.1); pesos não baixados |

## Software

- Hugging Face `transformers` 5.22.2: `TemperatureLogitsWarper`, `TopKLogitsWarper`, `TopPLogitsWarper`, `generate(do_sample=False)`.
- PyTorch `torch.softmax` / `torch.topk` — referência numérica.

## Tronco (citação, sem cópia)

- M01 aula, seção “LLM: amostragem, não oráculo”.
- Lab `exemplo-04-webai02-temperature-and-topK` (sliders; Prompt API).
- M01 embeddings de sentença / RAG Neo4j (`exemplo-12`, `exemplo-13`) — contraste com embedding de token.

## Leitura extra (Apache-2.0, isolada)

Módulo de tokenização/amostragem no [lucianoon/llm-course](https://github.com/lucianoon/llm-course) **não** está no recorte vendored. O texto desta aula é original.
