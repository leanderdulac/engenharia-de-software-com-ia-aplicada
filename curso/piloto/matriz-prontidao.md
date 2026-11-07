# Matriz de prontidão por módulo

Preenchida com **comandos reais desta estabilização**. Sem nota numérica de maturidade. Sem dados de alunos.

Legenda: **testado** = comando rodou aqui; **inspeção** = ficheiros lidos, sem executar o lab; **não testado** = fora do recorte desta máquina; **bloqueado** = precisa GPU, segredo, Docker de serviço ou download grande. Mock ≠ integração real.

Comandos de regressão (passaram nesta VM, Node v22.23.4):

```bash
node --test curso/avaliacao-colaboracao/verificar.test.mjs   # 11/11
npm --prefix curso/preview test                              # 21/21
npm --prefix curso/preview run check                         # fail=0
node curso/preview/e2e.mjs                                   # pass (Chrome CDP)
```

Build estático (`páginas=52 pdfs=45`) e smoke: [evidencias.md](./evidencias.md).

| Módulo | Recorte piloto | Estado | Evidência / bloqueio | Acção se bloquear |
| --- | --- | --- | --- | --- |
| Preview `curso/` | Home, módulos, aulas, PDF, TTS/VTT no disco | **testado** (HTTP + helpers + e2e Chrome) | `npm --prefix curso/preview test`; `node curso/preview/e2e.mjs` (home, `#/modulos/01.md`, aula + recarga, Apache isolado) | Sem Chrome: e2e SKIP exit 0 |
| Links internos `curso/` | Markdown do pacote | **testado** | `npm run check --prefix curso/preview` | — |
| C-COLAB | Verificador + fixtures | **testado** | 11 testes; vazamento PII → `reprovado_falha_critica` | — |
| M01 | C01.1 pasta/template | **inspeção** + patches | `.env.example` no ex. 11; curl MIME; e-commerce :3000; `test:docker` no alumnus. `exemplo-00-z` **não testado** (tfjs-node nativo). Web AI **bloqueado** (Chrome flags + hardware) | Instrutor: `npm start` no `exemplo-00-z` na máquina da sala |
| M02 | C02.1 lab 02 (sem LLM) | **testado** | `npm --prefix modulo02-integracao-apis-llms/02-langchain-intro test` — 3/3, sem `.env`, sem API. Labs OpenRouter **bloqueado** (segredo) | Chave só se a instituição fornecer |
| M03 | CipherSuite + Inspector CLI + Mongo CRUD | **testado** (local) | CipherSuite 4/4 (Node 22 e 24.22.1); Inspector `--cli tools/list`; Mongo `piloto-mongo` + CRUD 9/9; customers MCP 6/6 com API `:9999`. UI Inspector **não** aberta | UI 6274 na máquina da sala |
| M04 | OpsPilot | **bloqueado** (segredo) | `.env.example` em U2–U5. Sem chamada OpenRouter | Instituição decide chave `:free` |
| M05 | Pix compile + CFP Nx | **testado** (build) | `ng build` + vitest 4/4; `nx build frontend` + `nx build api`. a11y estática. Genkit **bloqueado** (chave) | BragBot: GEMINI_API_KEY |
| M06 | Nexus | **bloqueado** (segredo) | `GROQ_API_KEY`; Prometheus/Jaeger **simulados**. `.env.example` na raiz do módulo | Não chamar Groq no smoke; C06.4 só com chave institucional |
| M07 | Monte Carlo + RouteWise Jest | **testado** | `monte-carlo-routewise.js`; submódulo `npm test` 12/12 | Python Danger fora do submódulo |
| M08 | Ollama embeddings | **testado** (nomic) + **bloqueado** (gemma4) | Runtime Ollama + `nomic-embed-text` (768 dims). `gemma4:e2b` não puxado (~5 GB+). tinyllama só handshake generate | Lab ReAct continua a pedir gemma4 |
| M09 | Decision + GRPO math + contrato Vertex | **testado** (CPU) | decision 29/29; GRPO math 10/10; tinyllama generate handshake (≠ gemma4). Vertex recusa sem `GCP_PROJECT_ID`. LoRA/GPU **bloqueado** | Vertex: GCP_PROJECT_ID + TUNING_JOB_NAME |
| C05.2 Pix a11y | templates HTML | **testado** (estático) | `node curso/piloto/check-a11y-c052.mjs`. Não é WCAG; Angular **não** compilado; CFP **não** executado | Instrutor: teclado real no browser da sala |
| Companion Apache | RAG CPU | **bloqueado** (download) | `lab_cpu.py` pede torch + e5-small | Não misturar com o tronco; opcional depois |

## Não validado neste PR (escopo residual)

- Aprendizagem de alunos (ninguém foi recrutado).
- Qualidade de voz TTS / vídeo Grok / HeyGen (não ouvimos; VTT no disco).
- Labs E2E com Mongo, Neo4j, Postgres, k8s.
- GitHub Pages **publicado** (settings da conta + bloqueio jurídico ND).
- Autorização dos titulares para redistribuir adaptações.
- Python Danger local (`danger-config-routewise.py`) — não está no submódulo; Jest do submódulo **testado**.
- Angular Pix/CFP compilados e leitores de ecrã.
- Inspector MCP e Ollama `gemma4:e2b` **em execução** (só catálogo/comandos verificados).
- Autorização ND / Pages público.
