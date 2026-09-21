# Guia do instrutor

Como conduzir a trilha **deste** repositório, sem depender de conhecimento de corredor. Complementa [syllabus.md](./syllabus.md) e [avaliacao.md](./avaliacao.md).

## Papel do instrutor

Os vídeos não estão no Git. Sua função em sala é: **ordenar demos**, **impedir que a turma abra o `-z` cedo**, **traduzir READMEs errados** (M02/M03/M05) e **forçar curadoria** (diff vs exemplo). Não reescreva o curso: o código já é o material.

## Antes da primeira aula

1. Clone fresco; confirme que `modulo04-agentes-autonomos/` **não** existe — só `modulo04-criacao-de-agentes-autonomos-novo/`.
2. Suba um “lab canário”: `exemplo-00-z`, Ollama `exemplo-10`, e `python3 -c "import sys; print(sys.version)"` 3.10–3.13 para o M06.
3. Avise chaves: OpenRouter (M01–M04), Groq (M06), AI Studio (M05/M07), SerpAPI (M03 lab 02, opcional), GCP (M09, opcional), Chrome flags (M01 Web AI).
4. Windows: aponte WSL + [`troubleshooting/windows/`](../troubleshooting/windows/) + skill [`windowsfy`](../skills/windowsfy/SKILL.md). Não improvise `tfjs-node` no PowerShell 5 no primeiro dia.
5. Docker: `docker compose` com espaço ([`troubleshooting/docker.md`](../troubleshooting/docker.md)).
6. Distribua [guia-do-aluno.md](./guia-do-aluno.md) e o mapa; o README da raiz sozinho vira caça ao tesouro.

## O que enfatizar, por bloco

| Bloco | Ênfase em sala | Não enfatize |
| --- | --- | --- |
| M01 | Browser vs Node vs API; MCP como *contrato*; RAG como retrieval + geração | Treinar YOLO do zero; teoria profunda de transformers |
| M02 | Grafo como máquina de estados; guardrail **antes** do tool | LangSmith (opcional); README “article generator” |
| M03 | MCP server vs client vs Inspector; token na API legado | Publicar no npmjs público |
| M04 | Spec antes do agente; trace; autonomia **com** HITL | Fidelidade 100% ao roteiro HTML (não está no clone; `UNIDADE.md` registra desvios) |
| M05 | Prompt estruturado → artefato versionado; nomes reais de pasta | Firebase como se o BragBot usasse Hosting (usa Genkit) |
| M06 | Governança > “agente que aplica kubectl sozinho”; senha ChatOps | Cluster de produção; Prometheus real (tools são mock) |
| M07 | LLM **não** substitui Monte Carlo nem Danger; curadoria vs `output-exemplo` | Jira pago; Make.com obrigatório (há bot Node) |
| M08 | Agente vs regra; Approval Gate; canvas com **caso do aluno** | Copiar números do demo de RAG/cache |
| M09 | “Vale fine-tune?” primeiro; pesos LoRA fora do Git; custo Vertex | Prometer crédito GCP cobrindo generative AI |

## Ordem das demos (sala)

Demos curtas (10–20 min). O aluno reproduz depois. Não demonstre o gabarito inteiro.

### M01

1. Teachable Machine (link do README raiz) — 5 min, aquecimento.
2. `exemplo-00-z` vs template (diff de `index.js`).
3. `exemplo-01` parte01 → parte05 só no worker.
4. Duck Hunt parte02 (WebGL). Se a sala for fraca de GPU, pule e mostre o worker.
5. `exemplo-04` temperature/topK **no Chrome**; tenha [`troubleshooting/google.md`](../troubleshooting/google.md) aberto.
6. Playwright: leia `exemplo-06/prompts/generate-tests.md` e gere **um** teste — não o repo inteiro.
7. Grafana: `alumnus` + prompt `db-leaky-connections` (Docker pesado: suba antes da aula).
8. Ollama `request.sh` vs OpenRouter `request.sh` no mesmo prompt.
9. Neo4j template `script.txt` até o primeiro embedding; RAG (13) na aula seguinte.

### M02

1. Router: dois modelos, uma falha de chave.
2. LangGraph intro: **mostrar que não há LLM** — evita expectativa errada.
3. Medical: template stub → um nó preenchido → teste.
4. Safeguard `--unsafe` vs seguro (o momento pedagógico mais importante do módulo).
5. Cypher: `plan.md` na tela, README interno **não**.

### M03

1. Inspector no CipherSuite `-z`.
2. API CRUD no ar + MCP template vazio vs `-z`.
3. Lab 07: 401 sem token.
4. Verdaccio só se o tempo sobrar (Docker extra).

### M04

Siga **uma pasta por aula**. Não “git checkout” dentro do snapshot: cada pasta já é o fim da unidade.

1. U1: `/especificar` → código na Notas API (Copilot visível).
2. U2: `npm run arena -- --strategies react,plan-execute`.
3. U3: `POST /chat` + `npm run mcp`.
4. U4–U5: `conversa-longa.sh` e o evento `summarize`.
5. U6: chat sem `strategy`.
6. U7: `awaitHumanApproval: true` → 202.
7. U8: duas janelas (API + Vite).
8. U9: um incidente que força `handoff`.

Declare os desvios: `.env.example` some em U2–U5; U6/U7 compartilham commit; roteiro HTML ausente.

### M05

1. M1: um prompt de `prompts/` no AI Studio com `briefing-bruto.md`.
2. M2: HTML Stitch → componente Angular (não reconstrua o app).
3. M3: um workflow OpenSpec em `.agent/`.
4. M5: `flows.ts` + uma frase informal → brag.

### M06

Use o menu `nexus_iac_copilot.py`. Em sala:

1. Lab 2 (HCL) — resultado visível.
2. Lab 4: `kubectl apply` **antes** da fala.
3. Lab 6: `@nexus-bot destrua o banco` → senha.
4. Lab 12 no encerramento (demora; deixe rodar e narre o hierarchical).

Dashboard Streamlit é opcional; LocalStack só se já estiver no ar.

### M07

Uma ferramenta por encontro. Sempre: prompt → input RouteWise → **diff** com `output-exemplo-*`.

Obrigatório mostrar M4 scripts Monte Carlo (o LLM chuta P50; o script não) e M8 Danger `--local` com `pr-mock-falhas.json`.

### M08

Canvas no projetor, caso **da turma** (um aluno voluntário). Protótipo Ollama já puxado (`gemma4:e2b` é grande — baixe na véspera). Compare `audit-trail.jsonl`.

### M09

1. Tool de decisão nos 3 JSON — Atendimento reprova.
2. PII gate.
3. Não dispare Vertex “ao vivo” sem billing combinado. Mostre model card e Colab companion.
4. Capstone: leia `decisoes-de-arquitetura.md` e a regressão de formato documentada — honestidade > métrica bonita.

## Traps comuns (o que quebra a aula)

| Trap | Onde | O que fazer |
| --- | --- | --- |
| README diz porta 8080 | M01 e-commerce | É **3000** (`browser-sync`) |
| Prompt API some | M01 03–05 | `troubleshooting/google.md`; aceite fallback Ollama |
| `tfjs-node` no Windows | M01 00 | WSL ou skip para o 01 (browser) |
| `docker-compose` hífen | M01–M03 | `docker compose` |
| README “article generator” | M02 03/06, M03 02, vários MCP | Ignore; siga o guia `curso/modulos/` |
| Sem `.env.example` | M01 OpenRouter; M04 U2–U5 | Copie de U6+ ou de `exemplo-12-template` |
| Template 05 sem `tests/` | M02 safeguard | Avalie pelos scripts `chat:*` |
| Lab 07 M02 sem PDF | `07-doc-analysis` | Aluno traz PDF próprio |
| `07-…-template` contém pastas `*-z` | M03 | Compare **árvore irmã** `07-…-z/` |
| Firebase no discurso do M05 | README M05 | BragBot = Genkit + Google GenAI |
| Pastas `modulo-01-discovery-…` | README M05 | Disco = `modulo-01/` … `modulo-05/` |
| Groq 3.14 | M06 | Python 3.10–3.13 |
| Prometheus “de verdade” | M06 lab 4 | `tools/obs_tools.py` simula |
| PDFs de missão | M07–M09 | Use [avaliacao.md](./avaliacao.md) |
| Copiar limiar RAG do demo | M08 M4 | Canvas pede medição própria |
| `adapters.safetensors` | M09 M4 | Treinar; não estão no Git |
| Crédito GCP = Vertex | M09 README | Nem sempre; ler exclusões |
| Modelo Gemini aposentado | M09 | `risco-validade-modelo-companion.md` |
| Gabarito no primeiro `ls` | M01–M03 | Combinado de sala: template primeiro |

## Ritmo de turma (sugestão)

- Encontros síncronos: demo + 20 min de lab assistido + 5 min de “o que entregar no checkpoint”.
- Assíncrono: resto das horas da [trilha](./trilha-aprendizado.md).
- M04 U6 e U7 podem ser um único encontro (snapshots próximos).
- M03 labs 03–04 (instructions/skills) cabem colados na live 2026-02-24.
- M04 U1 cola na live 2026-05-27 (SDD).

## Comunicação de lacunas

Se o aluno perguntar “cadê o plano HTML / o PDF / o módulo 04 antigo”, aponte [lacunas-e-proximos-passos.md](./lacunas-e-proximos-passos.md) e siga. Não prometa pasta que não está no clone.
