# Lacunas e próximos passos

Inventário **honesto** do que o clone atual não entrega, para o pacote `curso/` não fingir material que não está no disco. Atualize este arquivo quando o repo ganhar os artefatos.

## Lacunas estruturais

| Item | Impacto | Como o curso contorna hoje |
| --- | --- | --- |
| README curto na raiz de M01, M02, M03 | Já apontam ao guia; labs M02/M03 têm README por pasta alinhado ao disco nesta estabilização | Manter os READMEs se o código mudar |
| Pasta `modulo04-agentes-autonomos/` (gravação antiga) **não existe** neste clone | Não há material legado para abrir | Só [`modulo04-criacao-de-agentes-autonomos-novo/`](../modulo04-criacao-de-agentes-autonomos-novo/) |
| Planos `unidade-N-plano-de-aula.html` (M04) ausentes | Instrutor sem roteiro minuto a minuto | `UNIDADE.md` em cada snapshot |
| `embaixadores/` vazio | Nada a ensinar | Ignorar |
| Vídeos fora do Git | Curso incompleto sem a plataforma da pós | Labs + este pacote |

## Módulos 02 e 03 (docs das pastas)

READMEs das pastas foram **reescritos para o disco** nesta rodada (comandos, env, testes existentes ou não). Residual:

- `package.json` do lab médico **ainda** se chama `prompt-chaining-article-generator` (description corrigida).
- Labs sem par template/gabarito: M02 `01`, `02`, `07`; M03 `02`, `08`, `09` — é o desenho do material, não um README mentiroso.
- M02 `07-doc-analysis`: PDF **existe** em `docs/` (~434K); pasta `tests/` **não**.
- M02 `05`: sem `tests/` e sem script `npm test` (README agora diz isso).
- M03 `01`: description do `package.json` corrigida; código = CSV de vendas.
- M03 `07-…-template` contém subpastas nomeadas `*-z` — README do lab 07 explica a armadilha.
- M03 `03` / `04`: material curto, sem app (README próprio).
- Inspector/Node: documentado no README do M03 (site ≥22.19.0; npm 2.14.0 `engines` `^22.23.4 || ^24.22.1 || >=26.12.1`; CipherSuite `v24.14.0`; UI 6274). **Não executámos** o Inspector nesta VM (precisa do servidor MCP + browser).

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

- README do módulo lista `modulo-01/` … `modulo-05/` (alinhado ao disco).
- Só `modulo-01/README.md` é pedagógico; 02–05 são README de Angular/Nx.
- Firebase citado no texto antigo do README; BragBot usa Genkit + `@genkit-ai/google-genai`.
- Typo `cfp-plataform_v1`.
- `.env.example` no BragBot (`GEMINI_API_KEY` / `GOOGLE_GENAI_API_KEY`). Sem chamada paga no smoke.

## Módulos 06–09

- M06: sem rubrica de nota; Prometheus/Jaeger simulados; `.env.example` na raiz do módulo (`GROQ_API_KEY=`). Smoke **não** chama Groq.
- M07: submódulo `routewise-danger-demo` inicializado neste clone (`7c52d76`); `npm test` Jest 12/12. Python Danger (`danger-config-routewise.py`) **não** está no submódulo. Missões PDF em `modulo-01-` … `modulo-10-`. Sem `jira-estado-board.md` em 08/09.
- M08/M09: cada submódulo tem `Atividade N - Módulo N.pdf` e `Exemplo - Módulo N.pdf` (M08 M1 também tem os canvases PDF e o cheat sheet de clouds).
- M09: `adapters.safetensors` propositalmente fora do Git; nomes de modelo Gemini envelhecem (`risco-validade-modelo-companion.md`).

## Lives e extras

- Lives são complemento. `2026-07-28` assume Claude Code mas o README lista agentes alternativos.
- CI do repo: `skills/` **e** `ci-curso-piloto.yml` (preview, C-COLAB, links internos, smoke offline). Labs com API/GPU continuam fora do verde.

## Prioridade residual (não fingir que está certificado)

1. Execução real de Inspector + Docker Mongo + Ollama na máquina da sala (aqui: **bloqueado**).
2. Revisão jurídica humana de LGPD/DPA (texto da lei citado; **não** há parecer).
3. WCAG completa / leitores de ecrã no Pix e CFP (aqui: checagem **estática** de templates Pix).
4. READMEs internos de M02 `04-song` snapshots se o código passar a LibSQL de novo.

A estabilização **reescreveu** os READMEs M02/M03 alinhados ao disco; Inspector/Ollama/LGPD/Vertex/GRPO/C05.2 atualizados com fontes oficiais. Não certifica aprendizagem.

Publicação pública (Pages) e autorização de titulares: [licencas/LEIA-ME.md](./licencas/LEIA-ME.md). Piloto: [piloto/protocolo.md](./piloto/protocolo.md).

## Material complementar agora no disco

Há um recorte Apache-2.0 em [`referencia/llm-course/`](../referencia/llm-course/) (RAG/LoRA/produção + `auditar_dataset`). **Não** são os 19 módulos do curso companheiro. Labs Amplitude/TrialForge/MCP **não** foram alterados. Ver [ATRIBUICOES-llm-course.md](./ATRIBUICOES-llm-course.md).

Há um checkpoint **opcional** de colaboração em [guia-checkpoint-colaboracao.md](./guia-checkpoint-colaboracao.md). É atividade didática de três fixtures, **não** o Collaborative Intelligence Benchmark (240 tarefas). Sem mídia nova.
