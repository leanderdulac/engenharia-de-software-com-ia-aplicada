# Lacunas e próximos passos

Inventário **honesto** do que o clone atual não entrega, para o pacote `curso/` não fingir material que não está no disco. Atualize este arquivo quando o repo ganhar os artefatos.

## Lacunas estruturais

| Item | Impacto | Como o curso contorna hoje |
| --- | --- | --- |
| README curto na raiz de M01, M02, M03 (só aponta ao guia) | Aluno ainda pode cair em README interno mentiroso | Guias [`modulos/01.md`](./modulos/01.md)–[`03.md`](./modulos/03.md) prevalecem |
| Pasta `modulo04-agentes-autonomos/` (gravação antiga) **não existe** neste clone | Não há material legado para abrir | Só [`modulo04-criacao-de-agentes-autonomos-novo/`](../modulo04-criacao-de-agentes-autonomos-novo/) |
| Planos `unidade-N-plano-de-aula.html` (M04) ausentes | Instrutor sem roteiro minuto a minuto | `UNIDADE.md` em cada snapshot |
| `embaixadores/` vazio | Nada a ensinar | Ignorar |
| Vídeos fora do Git | Curso incompleto sem a plataforma da pós | Labs + este pacote |

## Módulos 02 e 03 (mais finos / docs quebradas)

O código é usável; a **documentação interna mente**.

- READMEs copiados de um “Prompt Chaining Article Generator” em: `03-medical-appointment-*`, `06-rag-neo4j-students-template`, `02-google-trends-agent`, vários `customers-mcp-*` (texto CipherSuite em MCP de customers).
- `package.json` do medical ainda se chama `prompt-chaining-article-generator`.
- Labs sem par template/gabarito: M02 `01`, `02`, `07`; M03 `02`, `08`, `09`.
- M02 `07-doc-analysis`: scripts de teste sem pasta `tests/`; PDF referenciado **não** está em `docs/`.
- M02 `05-…-template`: README promete testes que não existem.
- M03 `01`: description do `package.json` fala SerpAPI; o lab é CSV de vendas + Mongo MCP.
- M03 `07-…-template` contém subpastas nomeadas `*-z` — confunde.
- M03 `03-dev-instructions-agents` e `04-skills`: material curto, sem app.

**Próximo passo (manutenção do repo):** um README verdadeiro por lab (propósito, env, comando, o que o template deixa vazio). Até lá, o guia do módulo prevalece sobre o README da pasta.

## Módulo 01

- Sem README/UNIDADE por exemplo (exceto e-commerce, Duck Hunt, Context7 demo, alumnus).
- `exemplo-06` e `exemplo-07` são só prompts — o aluno gera o projeto.
- `exemplo-11` agora tem `.env.example`; `Content-Type: application/json` no curl. **Ainda bloqueado** sem `OPENROUTER_API_KEY` (não chamar no smoke).
- README do **template** e-commerce aponta :3000 (os snapshots `-z` podem ainda citar 8080 no README interno / tasks).
- `exemplo-09` `test:docker` aponta para `infra/` na pasta `alumnus/` (não `apps/alumnus`).

## Módulo 04

- `.env.example` copiado para U2–U5 (mesmas chaves OpenRouter do U6). Não testa a API daqui.
- U6 e U7 agrupam commits; features do roteiro faltando estão listadas em cada `UNIDADE.md` (ex.: `graph:draw`, budget em USD no `/stats`, chat mode revisor).
- Frontend e Pages só U8+.

## Módulo 05

- README lista `modulo-01-discovery-refinement/` etc.; disco = `modulo-01/` … `modulo-05/`.
- Só `modulo-01/README.md` é pedagógico; 02–05 são README de Angular/Nx.
- Firebase citado; BragBot usa Genkit + `@genkit-ai/google-genai`.
- Typo `cfp-plataform_v1`.
- `.env.example` no BragBot (`GEMINI_API_KEY` / `GOOGLE_GENAI_API_KEY`). Sem chamada paga no smoke. README do módulo M05 ainda lista nomes de pasta longos — aviso no topo aponta `modulo-01/` … `modulo-05/`.

## Módulos 06–09

- M06: sem rubrica de nota; Prometheus/Jaeger simulados; `.env.example` na raiz do módulo (`GROQ_API_KEY=`). Smoke **não** chama Groq.
- M07: submódulo git `routewise-danger-demo` (`.gitmodules`) — clone com `--recurse-submodules` se a demo CI for usada. Missões `Atividade - Módulo N.pdf` e gabaritos `Exemplo - Módulo N.pdf` estão em cada pasta `modulo-01-` … `modulo-10-`. Não há `jira-estado-board.md` em `modulo-08-governanca-e-compliance/` nem em `modulo-09-automacao-de-ecossistema/` (existe em 01–07 e 10).
- M08/M09: cada submódulo tem `Atividade N - Módulo N.pdf` e `Exemplo - Módulo N.pdf` (M08 M1 também tem os canvases PDF e o cheat sheet de clouds).
- M09: `adapters.safetensors` propositalmente fora do Git; nomes de modelo Gemini envelhecem (`risco-validade-modelo-companion.md`).

## Lives e extras

- Lives são complemento. `2026-07-28` assume Claude Code mas o README lista agentes alternativos.
- CI do repo: `skills/` **e** `ci-curso-piloto.yml` (preview, C-COLAB, links internos, smoke offline). Labs com API/GPU continuam fora do verde.

## Prioridade se alguém for melhorar o material (não este PR)

1. README de verdade em cada lab M02/M03 (corrige a maior fonte de abandono).
2. Revisão humana especialista: nomes do MCP Inspector / engine Node; tags Ollama `gemma4`; LGPD/Vertex/GRPO no M09; a11y C05.2.
3. Alinhar README interno do M05 (ainda lista nomes longos; o aviso no topo aponta `modulo-01/` … `modulo-05/`). `.env.example` do BragBot e do exemplo 11 já estão no disco.

A estabilização do piloto **corrigiu blockers pontuais** (preview, rubrica C-COLAB, `.env.example`, typo MIME, `test:docker`, README âncora M01–M03). Não reescreveu READMEs mentirosos de M02/M03 por completo — o guia do módulo prevalece.

Publicação pública (Pages) e autorização de titulares: [licencas/LEIA-ME.md](./licencas/LEIA-ME.md). Piloto: [piloto/protocolo.md](./piloto/protocolo.md).

## Material complementar agora no disco

Há um recorte Apache-2.0 em [`referencia/llm-course/`](../referencia/llm-course/) (RAG/LoRA/produção + `auditar_dataset`). **Não** são os 19 módulos do curso companheiro. Labs Amplitude/TrialForge/MCP **não** foram alterados. Ver [ATRIBUICOES-llm-course.md](./ATRIBUICOES-llm-course.md).

Há um checkpoint **opcional** de colaboração em [guia-checkpoint-colaboracao.md](./guia-checkpoint-colaboracao.md). É atividade didática de três fixtures, **não** o Collaborative Intelligence Benchmark (240 tarefas). Sem mídia nova.
