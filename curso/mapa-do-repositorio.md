# Mapa do repositório

Pasta → aula/lab → **o que o aluno faz**. Caminhos relativos à raiz do Git. Só entra o que existe neste clone.

Legenda: **T** = template (trabalhe aqui); **Z** = gabarito; **S** = snapshot cumulativo; **L** = lab executável; **P** = prompts/canvas (não é app completo).

## Raiz

| Pasta / arquivo | Papel |
| --- | --- |
| [`curso/`](./README.md) | Pacote ensinável (você está aqui) |
| [`README.md`](../README.md) | Links de aula por submódulo |
| [`LICENSE.md`](../LICENSE.md) | CC BY-NC-ND 4.0 |
| [`troubleshooting/`](../troubleshooting/) | Docker, Chrome/Web AI, Windows/WSL |
| [`skills/windowsfy/`](../skills/windowsfy/) | Skill para adaptar scripts Unix → Windows |
| [`lives/`](../lives/) | Três lives (MCP, SDD, Safer) |
| [`embaixadores/`](../embaixadores/) | Vazio (`.gitkeep`) |
| [`.github/workflows/ci_test-skills.yml`](../.github/workflows/ci_test-skills.yml) | CI da skill windowsfy |
| [`.gitmodules`](../.gitmodules) | Submódulo Danger demo do RouteWise |

---

## Módulo 01 — `modulo01-fundamentos-de-ia-e-llms-para-programadores/`

Não há README na raiz desta pasta. O índice de aulas é o README da raiz do repo.

| Pasta | Tipo | Aula (README raiz) | O aluno faz |
| --- | --- | --- | --- |
| `exemplo-00-template/` | T | 1.3.1 | Completar treino TF.js Node em `index.js` |
| `exemplo-00-z/` | Z | 1.3.1 | Rodar classificador completo (`npm start`) e comparar |
| `exemplo-01-ecommerce-recomendations-template/` | T | 1.3.2 | UI + worker; `npm start` (browser-sync **:3000**, não 8080 do README interno) |
| `exemplo-01-ecommerce-recomendations-z/parte0{1-5}-*/` | Z | 1.3.2 | Seguir a evolução só de `modelTrainingWorker.js` |
| `exemplo-02-vencendo-qualquer-jogo/_template/` | T | 1.4 | Jogar Duck Hunt; inspecionar worker YOLO |
| `exemplo-02-vencendo-qualquer-jogo/DuckHunt-JS-parte01/` | Z | 1.4 | Worker com modelo carregado |
| `exemplo-02-vencendo-qualquer-jogo/DuckHunt-JS-parte02/` | Z | 1.4 | Detecção com threshold |
| `exemplo-03-webai01/` | L | 5.3 | Abrir `index.html` no Chrome com Prompt API |
| `exemplo-04-webai02-temperature-and-topK/` | L | 5.3 | `npm start`; variar temperature e topK |
| `exemplo-05-webai03-multimodal/` | L | 5.4 | Imagem/áudio + Translator API |
| `exemplo-06-playwright-testes/` | P | 8.2 | Usar prompts + `example.mcp.json` para **gerar** o projeto Playwright (não há `tests/` commitados) |
| `exemplo-07-playwright-navegacao/` | P | 8.3 | Seguir `prompt.md` (Form + Sessionize, **sem** submit) |
| `exemplo-08-context7/` | P+Z | 8.4 | `prompt.md` (gerar Next+Better Auth) **ou** rodar `nextjs-better-auth-demo/` |
| `exemplo-09-grafana-mcp/alumnus/` | L | 8.5 | Docker da stack + investigar leak com prompts em `docs/` |
| `exemplo-10-ollama/` | L | 9.2 | Executar `request.sh` com Ollama no ar |
| `exemplo-11-openrouter/` | L | 9.3 | `.env` com `OPENROUTER_API_KEY` + `request.sh` |
| `exemplo-12-embeddings-neo4j-template/` | T | 10.2 | Seguir `script.txt`; subir Neo4j (`docker compose`) |
| `exemplo-12-embeddings-neo4j/` | Z | 10.2 | Pipeline PDF → embeddings → Neo4j |
| `exemplo-13-embeddings-neo4j-rag/` | Z | 10.3 | RAG LangChain + OpenRouter; ler `respostas/` só depois |

---

## Módulo 02 — `modulo02-integracao-apis-llms/`

Sem README de módulo. Vários READMEs internos estão **errados** (texto de “article generator”); o código manda.

| Pasta | Tipo | O aluno faz |
| --- | --- | --- |
| `01-smart-model-router-gateway/` | L | Configurar modelos/provider sort; `POST /chat`; E2E |
| `02-langchain-intro/` | L | StateGraph upper/lower (**sem LLM** nos nós); `langgraph:serve` |
| `03-medical-appointment-template/` | T | Implementar nós de intent/agendamento |
| `03-medical-appointment-z/` | Z | Referência completa OpenRouter |
| `04-song-highlights-template/` | T | Memória + Postgres (`docker compose`) |
| `04-song-highlights-z/` | Z | Chat com preferências persistidas |
| `05-safeguard-prompt-injection-template/` | T | Guardrails; scripts `chat:member:unsafe:*` |
| `05-safeguard-prompt-injection-z/` | Z | Safeguard + MCP filesystem |
| `06-rag-neo4j-students-template/` | T | Seguir **`plan.md`** (não o README); seed Neo4j |
| `06-rag-neo4j-students-z/` | Z | Text-to-Cypher completo |
| `07-doc-analysis/` | L | Q&A PDF na porta 4000; **não há PDF em `docs/` neste clone** |

---

## Módulo 03 — `modulo03-mcp-na-pratica/`

| Pasta | Tipo | O aluno faz |
| --- | --- | --- |
| `01-multiple-mcp-tools-template/` | T | Ligar MCP (Mongo/FS) ao agente de vendas CSV |
| `01-multiple-mcp-tools-z/` | Z | Relatórios em `reports/` |
| `02-google-trends-agent/` | L | Tool SerpAPI; precisa `SERPAPI_API_KEY` |
| `03-dev-instructions-agents/` | P | Copiar `.github/agents/*.agent.md` para o IDE |
| `04-skills/` | P | Explorar `.agents/skills/` e `refs.txt` |
| `05-mcps-do-zero-template/` | T | Transformar crypto local em MCP (`src/mcp.ts` no Z) |
| `05-mcps-do-zero-z/` | Z | Inspector (`mcp:inspect`) |
| `06-your-legacy-api-as-mcp/nodejs-fastify-mongodb-crud/` | L | Subir CRUD `:9999` |
| `06-your-legacy-api-as-mcp/customers-mcp-template/` | T | Implementar tools CRUD no MCP |
| `06-your-legacy-api-as-mcp/customers-mcp-z/` | Z | Gabarito MCP |
| `07-api-security-auth-rate-limiting-template/` | T | Auth na API (JWT, roles, service token). Subpastas se chamam `*-z` mesmo no template — compare com a pasta irmã `07-…-z/` |
| `07-api-security-auth-rate-limiting-z/` | Z | API + MCP com `SERVICE_TOKEN` |
| `08-publishing-mcps-private-npm/` | L | Verdaccio `:4873`; `registry:*` / `release:private` |
| `09-using-mcp-with-langchain/` | Z | `MultiServerMCPClient` + API; só gabarito |

---

## Módulo 04 — `modulo04-criacao-de-agentes-autonomos-novo/`

Índice: [`README.md`](../modulo04-criacao-de-agentes-autonomos-novo/README.md). Cada pasta tem `UNIDADE.md`.

| Pasta | Tipo | O aluno faz |
| --- | --- | --- |
| `01-arquitetura-de-agentes-de-codigo/notas-api/` | S | Operar Copilot com specs em `specs/` |
| `02-padroes-de-raciocinio-e-execucao/` | S | `npm run arena`, `npm run bench` |
| `03-function-calling-e-tool-use/` | S | `npm run dev` + `npm run mcp` |
| `04-memoria-e-reflexao-em-agentes-autonomos/` | S | `/chat` com `conversationId`; `/memories` |
| `05-gerenciamento-de-contextos/` | S | `./scripts/conversa-longa.sh` |
| `06-langgraph-e-workflows-complexos/` | S | `/chat` **sem** `strategy` (roteador) |
| `07-observabilidade-e-limites-de-autonomia/` | S | HITL 202 + `GET /stats` |
| `08-projeto-pratico-opspilot-publicado/` | S | API `:3000` + `web/` `:5173` |
| `09-multi-agent-systems/` | S | Pedido que dispara rota `team` |

Planos HTML `unidade-N-plano-de-aula.html` são citados no README do módulo e **não estão neste clone**.

---

## Módulo 05 — `modulo05-ferramentas-de-IA-para-UI-UX/`

README interno lista nomes de pasta que **não batem** com o disco. Use esta tabela.

| Pasta real | O aluno faz |
| --- | --- |
| `modulo-01/` | Prompts em `prompts/` sobre `docs/refinement/briefing-bruto.md`; dados em `data/` |
| `modulo-02/pix-app/` | Prototipar (Stitch/Figma em `briefing/`, `stitch/`) e evoluir Angular |
| `modulo-03/cfp-platform/` | OpenSpec + `.agent/workflows/` no monorepo Nx |
| `modulo-04/cfp-plataform_v1/cfp-platform_v1/` | E2E / MCP (change `create-event-tests`) |
| `modulo-05/brag-bot/` | Genkit `src/flows.ts`; `POST /api/brag` |

---

## Módulo 06 — `modulo06-aiops-engenharia-agentica/`

Entrada: [`README.md`](../modulo06-aiops-engenharia-agentica/README.md), menu `python3 nexus_iac_copilot.py`, dashboard `streamlit run ui/app.py`.

| Artefato | O aluno faz |
| --- | --- |
| `labs/modulo1_foundation.py` | Desenhar S3 com compliance |
| `labs/modulo2_iac_copilot.py` | Gerar/auditar `main.tf` |
| `labs/modulo3_k8s_ops.py` | Manifesto + decisão Canary |
| `labs/modulo4_troubleshooting.py` | `kubectl apply -f k8s/deploy.yml` e diagnosticar |
| `labs/modulo5_aiops.py` | NL→PromQL + alerta preditivo |
| `labs/modulo6_chatops.py` | Streamlit; senha `GESTOR-APROVA` |
| `labs/modulo7_devsecops.py` | Triage `data/trivy.json` |
| `labs/modulo8_cicd.py` | Otimizar `data/workflow_lento.yaml` |
| `labs/modulo9_finops.py` | Zumbis em `data/inventario_cloud.json` |
| `labs/modulo10_remediation.py` | RAG em `data/runbook_db.md` |
| `labs/modulo11_guardrails.py` | Dry-run + `sim`/`nao` |
| `labs/modulo12_projeto_final.py` | Relatório hierárquico multi-domínio |
| `core/`, `tools/` | Código dos agentes/tools (leitura) |
| `k8s/` | Manifests didáticos |
| `ui/app.py` | Dashboard LocalStack/OPA |
| `slides/` | Marp teoria/demo |

---

## Módulo 07 — `modulo07-ferramentas-de-ia-para-gestao-de-projetos/`

Fluxo padrão: `*-prompt.md` no AI Studio → dados de entrada → comparar `output-exemplo-*`. PDFs de atividade são citados no README e **não estão neste clone**.

| Pasta | Ferramenta | O aluno faz |
| --- | --- | --- |
| `modulo-01-planejamento-e-escopo/` | Requirements Copilot | Transcrição → backlog; CSV Jira |
| `modulo-02-priorizacao-de-backlog/` | Backlog Scorer | RICE + WSJF |
| `modulo-03-cronograma-e-capacidade/` | Scheduling | Cronograma + what-if |
| `modulo-04-estimativas-e-previsoes/` | Probability Forecast | PERT; **Monte Carlo nos scripts** `monte-carlo-routewise.js/.py` |
| `modulo-05-riscos-e-aiops/` | Risk Monitor | Cockpit V/A/V |
| `modulo-06-reunioes-turbinadas/` | Meeting Digest | Ata + JSON Jira |
| `modulo-07-status-reports/` | Status Report | Três audiências |
| `modulo-08-governanca-e-compliance/` | Compliance + Danger | Checklist + `danger-config-routewise.py --local` |
| `modulo-09-automacao-de-ecossistema/` | NL to Workflow | Make.com **ou** `ecosystem-bot-template.js` |
| `modulo-10-portfolio-e-okrs/` | OKR Aligner | Validar OKRs + scorecard |

---

## Módulo 08 — `modulo08-arquitetura-de-sistemas-com-ia/`

| Pasta | O aluno faz |
| --- | --- |
| `modulo-01-fundamentos-ai-first/` | Canvas + `decision-framework-tool.js/.py` |
| `modulo-02-single-agent/` | Protótipo ReAct (Ollama `gemma4:e2b`) |
| `modulo-03-multi-agent/` | Fila de mensagens + seletor de padrão |
| `modulo-04-padroes-ai-especificos/` | Gateway + `audit-trail.jsonl` |
| `modulo-05-arquitetura-enterprise/` | Tiering, eval gate, guardrail; `audit-trail-tiering.jsonl` |

---

## Módulo 09 — `modulo09-processamento-de-dados-e-fine-tuning-de-modelos/`

Companions de disciplina na **raiz** da pasta (não dentro dos submódulos).

| Pasta / arquivo | O aluno faz |
| --- | --- |
| `modulo-01-decision-framework/` | 4 perguntas + AHP/NPV; `amplitude-seguros-casos.json` |
| `modulo-02-preparacao-datasets/` | OCR/JSONL/PII; imagens em `documentos-brutos/` |
| `modulo-03-fine-tuning-via-api/` | Vertex; `gcp-setup-companion.md`; dataset 200 linhas |
| `modulo-04-lora-e-peft/` | MLX ou Colab; ranks 4/8/16; pesos **não** estão no Git |
| `modulo-05-avaliacao-modelos/` | Harness A/B + estresse |
| `modulo-06-projeto-final/` | Assistente + dataset 3000 + `decisoes-de-arquitetura.md` |
| `casos-de-mercado-fine-tuning-companion.md` etc. | Leitura transversal |

---

## Lives, skills, troubleshooting

| Pasta | O aluno faz |
| --- | --- |
| `lives/2026-02-24/` | Ler `base-teorica/` (MCP, Agent Skills) |
| `lives/2026-05-27/000-pre-live/` vs `001-pos-live/` | Diff Spec Kit / catalog browse |
| `lives/2026-07-28/` | `npm ci`; landing Safer; `resources/prompts.md` |
| `troubleshooting/docker.md` | `docker compose` (espaço) |
| `troubleshooting/google.md` | Prompt API / Gemini Nano |
| `troubleshooting/windows/*` | nvm-windows, WSL, conflitos de shell |
| `skills/windowsfy/` | `/windowsfy <path>` em Windows nativo |
