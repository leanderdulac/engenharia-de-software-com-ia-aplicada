# Trilha de aprendizado

Ordem recomendada para um aluno que entra do zero neste repositório. Cada linha aponta para o **capítulo didático** em [`modulos/`](./modulos/) (conceito, lab, armadilha, ponte) e para as pastas reais.

**Não pule M01 § RAG e M03 MCP** se a meta é o OpsPilot (M04) ou o TrialForge (M08): eles reutilizam as mesmas ideias com outro produto.

```text
M01 fundamentos ─┬─► M02 APIs/LangGraph ─► M03 MCP ─► M04 OpsPilot
                 │                              │
                 │                              └─► M05 UI/UX (paralelo após M01 prompts)
                 │
                 ├─► M06 Nexus (após ReAct do M04 U2 ou em paralelo com M04 U2–U7)
                 ├─► M07 RouteWise (independente após M01 prompts; casa com M05 discovery)
                 ├─► M08 TrialForge (após M04 U2–U9 e M01 RAG)
                 └─► M09 Amplitude (após M01 embeddings; GCP/Colab no meio)
```

## Dependências

| Módulo | Depende de | Pode ser paralelo a |
| --- | --- | --- |
| 01 | Pré-requisitos de [README.md](./README.md) | — |
| 02 | M01 (OpenRouter, prompts, RAG Neo4j) | — |
| 03 | M01 § MCP + M02 LangGraph | M05 (depois de prompts) |
| 04 | M02 (grafo/tools) + M03 (MCP, instructions) | M06 a partir da U2 |
| 05 | M01 prompts/JSON | M07 (mesmo estilo AI Studio) |
| 06 | Conceito ReAct (M04 U2 ou paper); Python | M04 U3–U9 |
| 07 | M01 prompts | M05, M06 (governança) |
| 08 | M04 (agente) + M01 RAG + M03 MCP (conceitual) | M09 decisão “agente vs fine-tune” |
| 09 | M01 embeddings; maturidade para custo/GCP | Final da trilha |

Lives: [`lives/2026-02-24/`](../lives/2026-02-24/) **antes ou junto** de M03; [`lives/2026-05-27/`](../lives/2026-05-27/) **junto** de M04 U1; [`lives/2026-07-28/`](../lives/2026-07-28/) **junto** de M05.

## Sequência módulo a módulo

Tempos = estudo individual + lab (não incluem a duração do vídeo da aula).

### Módulo 01 — 36 h — [guia](./modulos/01.md)

| # | Unidade | Pasta | Horas | Resultado visível |
| --- | --- | --- | --- | --- |
| 1.1 | Intro ML / Teachable Machine | links no README da raiz (sem pasta) | 2 | Modelo no Teachable Machine |
| 1.2 | NN, DL, base | links no README | 2 | Vocabulário (camada, loss, epoch) |
| 1.3 | TF.js no Node + recomendação | `exemplo-00-*`, `exemplo-01-*` | 6 | Classificador + e-commerce recomendando |
| 1.4 | Web ML / Duck Hunt | `exemplo-02-vencendo-qualquer-jogo/` | 4 | Detecção YOLO no jogo |
| 1.5 | Genéticos / RL (teoria) | só links no README | 2 | Consegue explicar neuroevolução vs RL |
| 1.6 | Como LLMs funcionam | só links | 2 | Attention/embeddings em linguagem de engenheiro |
| 1.7 | Web AI | `exemplo-03` … `exemplo-05` | 4 | Prompt API + multimodal no Chrome |
| 1.8 | Prompt engineering + TOON | README §6 (sem pasta de código) | 2 | Prompt versionado e formato estruturado |
| 1.9 | Agentes de código (visão) | README §7 | 1 | Distingue Ask/Edit/Agent |
| 1.10 | MCP Playwright, Context7, Grafana | `exemplo-06` … `exemplo-09` | 6 | Testes gerados, form preenchido, leak investigado |
| 1.11 | Ollama + OpenRouter | `exemplo-10`, `exemplo-11` | 2 | Mesmo prompt local vs nuvem |
| 1.12 | Embeddings + RAG Neo4j | `exemplo-12-*`, `exemplo-13-*` | 5 | Q&A sobre PDF com citação do grafo |

**Checkpoint:** RAG do exemplo 13 responde a uma pergunta do `tensores.pdf` (do template 12) com retrieval visível.

### Módulo 02 — 24 h — [guia](./modulos/02.md)

| # | Lab | Pasta (trabalhe no `-template` quando existir) | Horas |
| --- | --- | --- | --- |
| 2.1 | Smart model router | `01-smart-model-router-gateway/` | 3 |
| 2.2 | LangGraph intro | `02-langchain-intro/` | 2 |
| 2.3 | Consultas médicas | `03-medical-appointment-template/` | 5 |
| 2.4 | Song highlights + memória | `04-song-highlights-template/` | 5 |
| 2.5 | Prompt injection / safeguard | `05-safeguard-prompt-injection-template/` | 4 |
| 2.6 | RAG Cypher alunos | `06-rag-neo4j-students-template/` + `plan.md` | 4 |
| 2.7 | Doc analysis | `07-doc-analysis/` | 1 |

**Checkpoint:** fluxo médico no `-z` como referência; no template, `identifyIntent` chama LLM e os testes E2E passam (chave OpenRouter).

### Módulo 03 — 24 h — [guia](./modulos/03.md)

| # | Lab | Pasta | Horas |
| --- | --- | --- | --- |
| 3.1 | Múltiplas tools MCP | `01-multiple-mcp-tools-template/` | 4 |
| 3.2 | Google Trends agent | `02-google-trends-agent/` | 2 |
| 3.3 | Dev instructions | `03-dev-instructions-agents/` | 1 |
| 3.4 | Skills | `04-skills/` | 1 |
| 3.5 | MCP do zero | `05-mcps-do-zero-template/` | 4 |
| 3.6 | API legado → MCP | `06-your-legacy-api-as-mcp/` | 4 |
| 3.7 | Auth + rate limit | `07-api-security-auth-rate-limiting-template/` | 4 |
| 3.8 | npm privado | `08-publishing-mcps-private-npm/` | 2 |
| 3.9 | MCP + LangChain | `09-using-mcp-with-langchain/` | 2 |

**Checkpoint:** `customers-mcp` fala com a API Fastify+Mongo; no lab 07 o MCP só entra com `SERVICE_TOKEN`.

### Módulo 04 — 36 h — [guia](./modulos/04.md)

Siga os snapshots **na ordem**. Cada pasta é o projeto **ao final** da unidade.

| U | Pasta | Horas | Novo |
| --- | --- | --- | --- |
| 1 | `01-arquitetura-de-agentes-de-codigo/` | 4 | Notas API + Copilot/SDD |
| 2 | `02-padroes-de-raciocinio-e-execucao/` | 4 | ReAct, arena, bench |
| 3 | `03-function-calling-e-tool-use/` | 4 | `/chat`, SQLite, MCP |
| 4 | `04-memoria-e-reflexao-em-agentes-autonomos/` | 4 | memória + refletor |
| 5 | `05-gerenciamento-de-contextos/` | 4 | sumarização + budget |
| 6 | `06-langgraph-e-workflows-complexos/` | 4 | grafo + fallback de modelo |
| 7 | `07-observabilidade-e-limites-de-autonomia/` | 4 | `/stats`, aprovação humana |
| 8 | `08-projeto-pratico-opspilot-publicado/` | 4 | war room + Pages |
| 9 | `09-multi-agent-systems/` | 4 | supervisor + blackboard |

**Checkpoint:** U8 com API + `web/` no ar; um pedido `awaitHumanApproval` aparece no war room. U9: um caso gera rota `team` e eventos `handoff`.

### Módulo 05 — 20 h — [guia](./modulos/05.md)

Pastas reais: `modulo-01/` … `modulo-05/` (os nomes longos do README interno **não existem** no disco).

| # | Pasta | Horas |
| --- | --- | --- |
| 5.1 | `modulo-01/` discovery Pix | 4 |
| 5.2 | `modulo-02/pix-app/` | 4 |
| 5.3 | `modulo-03/cfp-platform/` | 5 |
| 5.4 | `modulo-04/cfp-plataform_v1/` | 4 |
| 5.5 | `modulo-05/brag-bot/` | 3 |

### Módulo 06 — 28 h — [guia](./modulos/06.md)

Labs 1→12 em [`modulo06-aiops-engenharia-agentica/labs/`](../modulo06-aiops-engenharia-agentica/labs/). ~2 h cada, **4 h no lab 12**.

**Checkpoint:** relatório executivo do lab 12 (SRE + Sec + FinOps) gerado pelo Nexus Manager.

### Módulo 07 — 20 h — [guia](./modulos/07.md)

Uma ferramenta por pasta `modulo-01-…` até `modulo-10-…`. ~2 h cada.

**Checkpoint:** scorecard de portfólio (M10) usando o board RouteWise evolutivo (`jira-estado-board.md` nas pastas 01–07 e 10; **não** existe em 08 nem 09).

### Módulo 08 — 20 h — [guia](./modulos/08.md)

Cinco pastas `modulo-01-fundamentos-ai-first/` … `modulo-05-arquitetura-enterprise/`. ~4 h cada.

**Checkpoint:** canvas de enterprise preenchido **com caso próprio** + execução do protótipo de tiering (JS ou Python) comparada ao `audit-trail-tiering.jsonl`.

### Módulo 09 — 28 h — [guia](./modulos/09.md)

| # | Pasta | Horas |
| --- | --- | --- |
| 9.1 | `modulo-01-decision-framework/` | 4 |
| 9.2 | `modulo-02-preparacao-datasets/` | 5 |
| 9.3 | `modulo-03-fine-tuning-via-api/` | 5 |
| 9.4 | `modulo-04-lora-e-peft/` | 5 |
| 9.5 | `modulo-05-avaliacao-modelos/` | 4 |
| 9.6 | `modulo-06-projeto-final/` | 5 |

Quem não for usar Vertex: faça 9.1–9.2 + 9.4 (MLX/Colab) + harness local de 9.5 + capstone `--local` em 9.6. Documente a escolha.

### Lives — 4 h

| Live | Quando encaixar | Horas |
| --- | --- | --- |
| 2026-02-24 MCP e Skills | Antes de M03 | 1,5 |
| 2026-05-27 SDD | Com M04 U1 | 1,5 |
| 2026-07-28 Safer | Com M05 | 1 |

## Ritmos alternativos

- **Só backend/agentes:** M01 (pular Duck Hunt se o tempo apertar) → M02 → M03 → M04 → M08. Recupere M06 se a meta for ops.
- **Só produto/gestão:** M01 prompts → M05 → M07. Sem OpsPilot você perde o vocabulário de HITL que o M08 cobra.
- **Só plataforma:** M01 Grafana/Ollama → M04 U2–U7 → M06 → M08 M5.

Se uma pasta `*-template` estiver vazia de README, o guia do módulo descreve o que o código faz — confie no guia, não no README copiado (há vários desatualizados; ver [lacunas-e-proximos-passos.md](./lacunas-e-proximos-passos.md)).
