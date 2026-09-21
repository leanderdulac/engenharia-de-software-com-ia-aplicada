# Guia do aluno

Como estudar **este** repositório do zero até o M09 sem depender de recado de grupo. Entrada: [README.md](./README.md). Ordem: [trilha-aprendizado.md](./trilha-aprendizado.md).

## 1. Setup (faça uma vez)

### Obrigatório para o M01

- Git.
- **Node.js 22** (vários labs pedem 22.x; Duck Hunt pede > 20; Grafana alumnus pede ≥ 22).
- npm.
- Editor com agente (Cursor, VS Code + Copilot, etc.).
- Docker Desktop ou engine + plugin Compose v2.
- Google Chrome atualizado (Web AI).

### Conforme a trilha avança

| Quando | O quê |
| --- | --- |
| M01 §9–10 | [Ollama](https://ollama.com/) local; conta [OpenRouter](https://openrouter.ai/) |
| M01 §8.5, M02–M03 | Docker: Neo4j, Postgres, Mongo, stack Grafana |
| M03 lab 02 | `SERPAPI_API_KEY` (pule o lab se não tiver) |
| M04 | Mesma chave OpenRouter; Copilot ou agente equivalente na U1 |
| M05 / M07 | [Google AI Studio](https://aistudio.google.com/) |
| M06 | Python **3.10–3.13**, `kubectl`, chave [Groq](https://groq.com/) |
| M08 | Ollama + `ollama pull gemma4:e2b` (vários GB; baixe **antes** da semana) |
| M09 | Conta GCP **ou** Mac Apple Silicon **ou** Colab (T4). Leia o README do M09 sobre custo |

Clone:

```bash
git clone https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada.git
cd engenharia-de-software-com-ia-aplicada
```

Trabalhe num **fork** ou clone pessoal ([LICENSE.md](../LICENSE.md): estudo, sem uso comercial). Não abra PR externo neste repositório.

### Windows

Caminho recomendado: **WSL** — [`troubleshooting/windows/wsl.md`](../troubleshooting/windows/wsl.md).

Se for nativo:

- [`troubleshooting/windows/commons.md`](../troubleshooting/windows/commons.md)
- Skill: [`skills/windowsfy/SKILL.md`](../skills/windowsfy/SKILL.md)

```sh
npx -y skills add https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada --skill windowsfy
```

Depois, no agente: `/windowsfy ./` ou `/windowsfy <pasta do exemplo>`.

### Docker

Use `docker compose` (espaço), não `docker-compose`. Detalhes: [`troubleshooting/docker.md`](../troubleshooting/docker.md).

### Chrome / Prompt API

Se `LanguageModel` falhar: [`troubleshooting/google.md`](../troubleshooting/google.md). Não trave o módulo: siga Ollama/OpenRouter e documente o fallback no checkpoint C01.2.

## 2. Convenções do repo

- **`*-template`**: você implementa. Stubs de propósito.
- **`*-z`**: gabarito. Abra **depois** de quebrar a cabeça (a nota desconta cola precoce — [avaliacao.md](./avaliacao.md)).
- **M04**: cada pasta `01-…` … `09-…` é um **snapshot no fim da unidade**, não um diff. Leia `UNIDADE.md` antes de `npm ci`.
- **M05**: no disco as pastas são `modulo-01/` … `modulo-05/`, não os nomes longos do README interno.
- **M07–M09**: cada pasta de unidade tem `Atividade` (missão) e `Exemplo` (gabarito) em PDF — ver [mapa](./mapa-do-repositorio.md) e os guias [`modulos/07.md`](./modulos/07.md)–[`09.md`](./modulos/09.md). Entregue **a Atividade ou** o checkpoint de [avaliacao.md](./avaliacao.md), não os dois. `*-prompt.md` / `*-canvas.md` / `*-tool.js` continuam sendo o lab.

Links de vídeo e papers extras: [README da raiz](../README.md). Comece sempre pelo guia em [`modulos/`](./modulos/).

## 3. Como estudar cada unidade

1. Leia os **objetivos** do guia do módulo (são mensuráveis — você sabe quando acabou).
2. Assista ao vídeo da aula (fora do Git), se a turma tiver.
3. Abra a pasta da [trilha](./trilha-aprendizado.md); instale só aquela pasta (`npm ci` / `pip` no venv do M06).
4. Faça a atividade do guia **no template** ou no canvas vazio.
5. Compare com `-z`, `output-exemplo-*`, `respostas/` ou `audit-trail*.jsonl`.
6. Marque o **checklist** do módulo; arquive a evidência do checkpoint.

Não instale o monorepo inteiro. Não rode `npm ci` na raiz (não há `package.json` raiz de aplicação).

## 4. Ritmo

- **6–8 h por semana** cobre ~um terço do M01 ou um lab médio. A trilha de 240 h é carga de pós, não de tutorial de fim de semana.
- Bloqueios de ambiente: 30 min no troubleshooting + windowsfy; depois pergunte no canal da turma com **pasta + comando + erro**.
- Se OpenRouter estiver fora: Ollama no M01/M08; Groq só no M06; M09 tem Colab.

Atalhos honestos (documente no entregável):

- Pular Duck Hunt se não houver WebGL.
- Pular SerpAPI (M03.02).
- M09 sem Vertex: decisão + dataset + LoRA Colab + harness local.

Não pule: RAG M01, guardrails M02, token MCP M03, HITL M04 ou M06, Monte Carlo script M07, canvas próprio M08, “vale fine-tune?” M09.

## 5. Chaves e `.env`

Nunca commite chave. Padrões que o material espera:

| Variável | Módulos |
| --- | --- |
| `OPENROUTER_API_KEY` | 01 (11–13), 02, 03, 04 |
| `GROQ_API_KEY` | 06 (`core/llm_config.py`) |
| `SERPAPI_API_KEY` | 03 lab 02 |
| `LANGSMITH_API_KEY` / tracing | opcional M02–M03 |
| `SERVICE_TOKEN` | 03 labs 07 e 09 |
| `GCP_PROJECT_ID`, `TUNING_JOB_NAME`, `ENDPOINT_MODULO32`, `ENDPOINT_MODULO63` | 09 |
| GitHub OAuth | demo Better Auth (M01 exemplo 08) |

`exemplo-11` **não tem** `.env.example`: crie `.env` com `OPENROUTER_API_KEY=...`. OpsPilot U2–U5: o README pede `cp .env.example .env` mas o arquivo **falta** nesses snapshots — copie o de [U6](../modulo04-criacao-de-agentes-autonomos-novo/06-langgraph-e-workflows-complexos/) e preencha.

## 6. Troubleshooting (ponteiro)

| Sintoma | Arquivo |
| --- | --- |
| Compose v1 / `version:` obsoleto | [`troubleshooting/docker.md`](../troubleshooting/docker.md) |
| Prompt API / Gemini Nano | [`troubleshooting/google.md`](../troubleshooting/google.md) |
| `tfjs-node`, `better-sqlite3`, aspas, globs no Windows | [`troubleshooting/windows/commons.md`](../troubleshooting/windows/commons.md) |
| Qual shell estou usando | [`troubleshooting/windows/conflicts.md`](../troubleshooting/windows/conflicts.md) |
| `ModuleNotFoundError: crewai` | venv do M06 (README do módulo) |
| Modelo Vertex sumiu | [`modulo09-…/risco-validade-modelo-companion.md`](../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/risco-validade-modelo-companion.md) |

## 7. Integridade acadêmica

Gabarito existe para **aprender o delta**, não para entregar o `-z` rebatizado. Canvases do M08 e OKRs do M07 devem ser do **seu** caso ou uma curadoria explícita do RouteWise/TrialForge. Licença: atribuição, não comercial, sem derivados redistribuídos — [LICENSE.md](../LICENSE.md).
