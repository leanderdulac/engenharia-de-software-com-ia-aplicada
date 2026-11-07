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
| M03 | Inspector / token | **inspeção** + **bloqueado** (Docker) | Comando oficial `npx @modelcontextprotocol/inspector` (porta 6274). Site MCP ≥22.19.0; npm 2.14.0 `engines` `^22.23.4 \|\| ^24.22.1 \|\| >=26.12.1`. CipherSuite `v24.14.0`. Inspector **não** foi aberto nesta VM | Monitor com Docker; documentar engine |
| M04 | OpsPilot | **bloqueado** (segredo) | `.env.example` em U2–U5. Sem chamada OpenRouter | Instituição decide chave `:free` |
| M05 | C05.1 pasta | **inspeção** | README do módulo com `modulo-01/` … `modulo-05/`. BragBot `.env.example`. Genkit **bloqueado** (chave) | Pix/CFP sem chave no recorte mínimo |
| M06 | Nexus | **bloqueado** (segredo) | `GROQ_API_KEY`; Prometheus/Jaeger **simulados**. `.env.example` na raiz do módulo | Não chamar Groq no smoke; C06.4 só com chave institucional |
| M07 | Monte Carlo | **testado** (script) | `node monte-carlo-routewise.js` no smoke | PDFs Atividade: servidos no preview `/arquivos/` |
| M08 | ReAct / Ollama | **bloqueado** (runtime) | Tag `gemma4:e2b` **existe** no catálogo oficial (4,6–7,5 GB); **não** puxámos o modelo. Sem Ollama nesta VM. C-COLAB cobre HITL sem Ollama | `ollama pull` na máquina da sala **ou** `provedores-pagos` |
| M09 | Decision tool + GRPO math | **testado** (CPU) | `decision-framework-tool.js` (29/29). GRPO: 10 testes de matemática **pass**; rollout Ollama **bloqueado**. Vertex **bloqueado** (segredo). LGPD: revisão documental da lei, não execução | C09.3 Colab institucional; não baixar modelos aqui |
| C05.2 Pix a11y | templates HTML | **testado** (estático) | `node curso/piloto/check-a11y-c052.mjs`. Não é WCAG; Angular **não** compilado; CFP **não** executado | Instrutor: teclado real no browser da sala |
| Companion Apache | RAG CPU | **bloqueado** (download) | `lab_cpu.py` pede torch + e5-small | Não misturar com o tronco; opcional depois |

## Não validado neste PR (escopo residual)

- Aprendizagem de alunos (ninguém foi recrutado).
- Qualidade de voz TTS / vídeo Grok / HeyGen (não ouvimos; VTT no disco).
- Labs E2E com Mongo, Neo4j, Postgres, k8s.
- GitHub Pages **publicado** (settings da conta + bloqueio jurídico ND).
- Autorização dos titulares para redistribuir adaptações.
- Submódulo `routewise-danger-demo`.
- Angular Pix/CFP compilados e leitores de ecrã.
- Inspector MCP e Ollama `gemma4:e2b` **em execução** (só catálogo/comandos verificados).
- Autorização ND / Pages público.
