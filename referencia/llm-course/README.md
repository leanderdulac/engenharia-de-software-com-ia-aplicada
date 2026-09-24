# Referência vendored — llm-course (Apache-2.0)

Recorte **mínimo** do curso aberto *Engenharia e Customização de LLMs em Português* (Luciano de Oliveira Nunes). Isolado de propósito: o tronco desta pós continua [CC BY-NC-ND 4.0](../../LICENSE.md).

Atribuição completa: [`curso/ATRIBUICOES-llm-course.md`](../../curso/ATRIBUICOES-llm-course.md).

## Origem

| Campo | Valor |
| --- | --- |
| Autor | Luciano de Oliveira Nunes |
| Upstream | https://github.com/lucianoon/llm-course |
| Fork usado | https://github.com/leanderdulac/curso-de-engenharia-de-IA |
| Licença | [Apache-2.0](./LICENSE) — [NOTICE](./NOTICE) intactos |
| Commit do clone | [SOURCE-COMMIT.txt](./SOURCE-COMMIT.txt) |

Não é um submodule. É vendor seletivo para estudo **ao lado** dos módulos 08 e 09 da pós (TrialForge e Amplitude), não no lugar deles.

## Por que estes arquivos

A pós já cobre RAG (M01/M08), LoRA (M09), eval (M08 eval gate + M09 harness) e PII (Amplitude M2) em TypeScript/Python de produto. O curso B aprofunda o **mesmo ciclo em Python de laboratório**: hipótese → medição → limite.

| Pasta / arquivo | Papel nesta pós | Roda neste recorte? |
| --- | --- | --- |
| [`modulo-13-rag/`](./modulo-13-rag/) | RAG do zero (BM25, denso, RRF, hit@k) — lê depois do TrialForge M4 | Leitura sim; execução completa pede os READMEs dos módulos 01–12 de B |
| [`modulo-06-lora/`](./modulo-06-lora/) | LoRA/NF4 do zero — lê junto do Amplitude M4 | `lab_cpu.py` pede MiniGPT + corpus do módulo 03 de B; `lab_mlx.py` é Mac + SFT de B |
| [`modulo-19-producao/`](./modulo-19-producao/) | Serving, custo, disjuntor, eval-as-CI — lê com TrialForge M5 | **Sim**, com as tools vendored (FAQ de brinquedo) |
| [`tools/auditar_dataset.py`](./tools/auditar_dataset.py) | Manifesto + scanner de e-mail/CPF/telefone | **Sim** (`governanca.py` incluso) |
| [`docs/`](./docs/) | Governança de dados e protocolo de avaliação | Texto; sem execução |

`tools/rag.py`, `tools/producao.py`, `tools/respostas.py` e `tools/minigpt.py` existem só porque os labs acima os importam. O restante de `tools/` de B **não** veio.

## Como usar

A partir desta pasta:

```bash
cd referencia/llm-course
PYTHONPATH=. python3 -m tools.auditar_dataset \
  ../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-02-preparacao-datasets/dataset-amplitude-seguros.jsonl \
  --nome amplitude-demo \
  --origem "Amplitude Seguros, sintético, tronco UniPDS" \
  --licenca "CC BY-NC-ND 4.0 (dataset do tronco; a tool é Apache-2.0)" \
  --finalidade "auditoria pedagógica antes do C09.2" \
  --saida /tmp/amplitude-dataset-manifest.json
```

Exit code `2` = o scanner achou PII: o manifesto é gravado, o gate falha. Não copie o valor sensível para log ou issue.

Lab de produção (o mais autônomo deste recorte):

```bash
cd referencia/llm-course
PYTHONPATH=. python3 modulo-19-producao/lab_cpu.py
```

Para RAG/LoRA **end-to-end** (corpus MiniGPT, READMEs 01–12, dados SFT), clone B:

```bash
git clone https://github.com/leanderdulac/curso-de-engenharia-de-IA.git
# ou https://github.com/lucianoon/llm-course.git
```

Rota sugerida (opcional, fora das 240 h): [trilha de aprofundamento](../../curso/trilha-aprendizado.md#aprofundamento-llm-python-opcional).

## O que este recorte não é

- Não são os 19 módulos de B.
- Não substitui os labs Amplitude (JS/Python) nem os protótipos TrialForge.
- Não muda rubrica: checkpoints continuam em [`curso/avaliacao.md`](../../curso/avaliacao.md).
- Dependências extras dos labs B (`torch`, `tokenizers`, `mlx`) **não** entram no `package.json` da pós. Instale só se for rodar o lab Python.

## Licença

Arquivos desta pasta (exceto este README de empacotamento) seguem Apache-2.0 e o NOTICE do autor. Este README descreve o vendor; o crédito legal está no `LICENSE` + `NOTICE` + SPDX no topo de cada cópia.
