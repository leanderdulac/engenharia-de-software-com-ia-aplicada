# NOTICE — Trilha Avançada

Obra nova desta pasta: autoria a definir na licença (ver [`LICENSE-PENDENTE.md`](./LICENSE-PENDENTE.md)).

Este produto inclui referências, trechos curtos de adaptação e dependências de terceiros. Esses trabalhos **mantêm as próprias licenças** e não são relicenciados pela trilha nem pelo tronco UniPDS.

## Jane Street — tutor socrático (MIT)

O arquivo [`tutor/tutor-socratico-ptbr.md`](./tutor/tutor-socratico-ptbr.md) é uma adaptação em português da skill `socratic-tutor` de Jane Street (`https://github.com/janestreet/agent_skills`, pasta `socratic-tutor/`).

```
The MIT License

Copyright (c) 2026 Jane Street Group, LLC <opensource-contacts@janestreet.com>
```

O texto MIT completo está no próprio arquivo do tutor. Esta adaptação **não** é um produto oficial da Jane Street.

## Luciano de Oliveira Nunes — llm-course (Apache-2.0)

Leitura extra opcional, **não vendored nesta pasta**:

- Upstream: https://github.com/lucianoon/llm-course
- Fork usado no repo: https://github.com/leanderdulac/curso-de-engenharia-de-IA
- Recorte já presente no clone: [`referencia/llm-course/`](../../referencia/llm-course/) (módulos 06, 13, 19 + tools)
- Crédito: [`curso/ATRIBUICOES-llm-course.md`](../ATRIBUICOES-llm-course.md)
- SPDX e NOTICE originais: [`referencia/llm-course/LICENSE`](../../referencia/llm-course/LICENSE), [`referencia/llm-course/NOTICE`](../../referencia/llm-course/NOTICE)

O módulo A2 aponta o **módulo 02** desse curso (atenção) como aprofundamento. A11 pode apontar módulos de quantização/serving do mesmo curso. Esses módulos **não** estão no recorte vendored; quem quiser lê no repositório B. O texto, os labs e os testes de A2 e A11 são originais desta trilha.

## Modelos e tokenizers (Hugging Face)

Os labs baixam pesos em tempo de execução. Cada modelo traz a licença no card:

| Modelo | Card | Licença lida no card (nov/2026) | Onde |
| --- | --- | --- | --- |
| `HuggingFaceTB/SmolLM2-135M` | https://huggingface.co/HuggingFaceTB/SmolLM2-135M | Apache-2.0 | A2, A11 (PTQ/KV) |
| `Qwen/Qwen2.5-0.5B` (opcional, `TRILHA_A2_MODELO=...`) | https://huggingface.co/Qwen/Qwen2.5-0.5B | Apache-2.0 | A2 |
| `ibm-granite/granite-3.1-1b-a400m-instruct` | https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct | Apache-2.0 | A11 (MoE real) |
| `allenai/OLMoE-1B-7B-0924-Instruct` | https://huggingface.co/allenai/OLMoE-1B-7B-0924-Instruct | Apache-2.0 | A11 (só config nesta CPU) |

## Papers (citação acadêmica, não código)

Ver [`modulo-a2/referencias.md`](./modulo-a2/referencias.md) e [`modulo-a11/referencias.md`](./modulo-a11/referencias.md). Citar um paper não transfere a licença do artigo para esta pasta.

## Tronco UniPDS (CC BY-NC-ND 4.0)

A trilha **cita** pastas e checkpoints de M01–M09 (por exemplo o lab de temperature do M01 e o LoRA do M09) sem copiar nem editar esses arquivos. O caso Amplitude Seguros é o mesmo da pós; datasets JSONL do M09 não são republicados aqui.
