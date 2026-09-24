# Atribuições — curso companheiro de engenharia de LLMs

Material **complementar e isolado**. Não substitui os nove módulos da pós UniPDS nem altera a licença do tronco.

## Crédito

O recorte em [`referencia/llm-course/`](../referencia/llm-course/) vem do curso aberto **Engenharia e Customização de LLMs em Português**, de **Luciano de Oliveira Nunes**.

| Item | Onde |
| --- | --- |
| Repositório original | [lucianoon/llm-course](https://github.com/lucianoon/llm-course) |
| Fork usado nesta integração | [leanderdulac/curso-de-engenharia-de-IA](https://github.com/leanderdulac/curso-de-engenharia-de-IA) |
| Licença do material companheiro | **Apache License 2.0** — cópia intacta em [`referencia/llm-course/LICENSE`](../referencia/llm-course/LICENSE) e [`NOTICE`](../referencia/llm-course/NOTICE) |
| Citação do autor | ver `CITATION.cff` no repositório original (Nunes, Luciano de Oliveira) |

## O que foi vendored neste clone

Cópia **mínima**, não os 19 módulos. Objetivo: aprofundar avaliação, LoRA, RAG, serving e governança de dados em Python, sem fundir o curso B no tronco TypeScript da pós.

| Caminho em `referencia/llm-course/` | Por quê |
| --- | --- |
| `LICENSE`, `NOTICE` | Obrigatório para redistribuir Apache-2.0 |
| `modulo-13-rag/` | Lab CPU de RAG (chunking, BM25, denso, RRF, hit@k) |
| `modulo-06-lora/` | Lab CPU de LoRA/quantização (MLX opcional, Mac) |
| `modulo-19-producao/` | Lab CPU de serving, custo, disjuntor, eval-as-CI |
| `tools/auditar_dataset.py` + `tools/governanca.py` | Scanner de PII + manifesto de proveniência |
| `tools/rag.py`, `tools/producao.py`, `tools/respostas.py`, `tools/minigpt.py` | Dependências mínimas que os labs importam |
| `docs/GOVERNANCA-DE-DADOS.md`, `docs/PROTOCOLO-DE-AVALIACAO.md` | Texto curto de gate de dados e protocolo de eval |

O que **não** foi copiado: Fase 0, módulos 01–05, 07–12 e 14–18, notebooks, `uv.lock`, CI e o restante de `tools/`. Para a trilha completa, use o repositório B.

Hash do commit clonado do fork: ver [`referencia/llm-course/SOURCE-COMMIT.txt`](../referencia/llm-course/SOURCE-COMMIT.txt).

## O que será (e o que não será) vendored

- **Já neste PR:** o recorte da tabela acima.
- **Fora de escopo:** fundir os 19 módulos no tronco `curso/` ou `modulo01`–`modulo09`; espalhar código Apache pelas pastas da Amplitude, TrialForge, OpsPilot, Nexus ou RouteWise; regenerar TTS/vídeo.
- **Futuro possível (outro PR):** mais um lab CPU pontual (por exemplo avaliação do módulo 14 de B), sempre isolado em `referencia/llm-course/` e citado aqui.

## Aviso de licenças (duas árvores)

| Árvore | Licença | Pode |
| --- | --- | --- |
| Tronco UniPDS (`curso/`, `modulo01`–`modulo09`, `lives/`, `skills/`, …) | [CC BY-NC-ND 4.0](../LICENSE.md) | Estudo; **sem** uso comercial; **sem** redistribuir derivados do tronco |
| Ilha Apache (`referencia/llm-course/`) | Apache-2.0 (Luciano de Oliveira Nunes) | Seguir o `LICENSE` **dessa pasta** — a UniPDS **não** relicencia esse material como CC BY-NC-ND |

Texto adaptado no pacote `curso/` (trilha, avaliação, guias M08/M09) é redação própria desta pós, com **citação** a B — não é cópia dos 19 módulos. Código Apache permanece só em `referencia/llm-course/`.

Leia o README da ilha: [`referencia/llm-course/README.md`](../referencia/llm-course/README.md). A trilha opcional está em [trilha-aprendizado.md](./trilha-aprendizado.md#aprofundamento-llm-python-opcional).
