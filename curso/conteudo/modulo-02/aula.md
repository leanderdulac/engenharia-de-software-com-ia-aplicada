![Capa do Módulo 02 — Integração de APIs de LLMs](../../media/imagens/modulo-02-capa.png)

# Módulo 02 — Integração de APIs de LLMs

Guia: [`curso/modulos/02.md`](../../modulos/02.md). Pasta: [`modulo02-integracao-apis-llms/`](../../../modulo02-integracao-apis-llms/). Carga: ~24 h.

Aviso que o guia já dá e esta aula repete de propósito: **não há README de módulo**, e vários READMEs de pasta falam de um “gerador de artigos” que não é este código. O `package.json` do lab médico ainda pode se chamar `prompt-chaining-article-generator`. Spec é o guia, o `plan.md` do lab 06, e os arquivos em `src/`.

---

## Abertura

No Módulo 01 o LLM era uma chamada. Você comparou Ollama e OpenRouter, indexou um PDF, viu trechos voltarem. Agora o modelo precisa viver **atrás de um contrato seu**: HTTP, grafo, banco, autorização.

A pergunta desta semana não é “qual o melhor modelo?”. É: quem escolhe o modelo, quem guarda o estado, quem impede o usuário de ler um arquivo, e quem corrige um Cypher inválido antes de bater no Neo4j.

Sete labs. Nem todos chamam LLM. O segundo, de propósito, classifica `upper`/`lower` **por palavra-chave**. Se você sair daqui achando que LangGraph é sinônimo de GPT, o lab 02 falhou — e vale refazer.

Ao final você deve conseguir:

- expor um gateway Fastify que escolhe provider/modelo no OpenRouter;
- desenhar um StateGraph com nós e arestas condicionais;
- completar o fluxo de agendamento médico no **template** (intent → serviço → mensagem);
- persistir preferência de usuário;
- mostrar um bloqueio de prompt injection e um caso privilegiado que passa;
- gerar Cypher contra um grafo de cursos **ou** perguntar a um PDF seu no lab 07.

---

## Conceitos (colados nestes labs)

### Gateway: o provedor não é a sua API

Em [`01-smart-model-router-gateway/`](../../../modulo02-integracao-apis-llms/01-smart-model-router-gateway/) o projeto é único — sem par template/gabarito. Leia `src/server.ts` e `src/openrouterService.ts`. O contrato do cliente é `POST /chat`. Quem conhece OpenRouter é o serviço. Quem conhece a lista de modelos é `src/config.ts`.

Por que isso importa: no M04 o OpsPilot inteiro aponta a fábrica de modelo para o OpenRouter, inclusive `:free`. No M08 o TrialForge desenha o mesmo padrão com nome de arquitetura — Gateway → Orquestrador → Modelo. Aqui você **implementa** o pedaço Gateway e valida com E2E (`npm test`, `tests/router.e2e.test.ts`). Force um modelo inválido. Veja fallback ou erro. Isso é aula, não acidente.

A chave `OPENROUTER_API_KEY` entra em todo lab que chama LLM. LangSmith é opcional.

### Grafo sem LLM (e grafo com domínio)

[`02-langchain-intro/`](../../../modulo02-integracao-apis-llms/02-langchain-intro/) monta um StateGraph em `src/graph/`. Os nós não pedem token: classificam texto em `upper`/`lower` por regra. `langgraph.json` + `npm run langgraph:serve` sobem o studio. O vocabulário que você precisa — **estado**, **nó**, **aresta**, **aresta condicional** — cabe neste lab barato. Guarde-o. O lab 03 só acrescenta um modelo no meio.

O lab médico é o primeiro grafo de negócio:

- Template: [`03-medical-appointment-template/`](../../../modulo02-integracao-apis-llms/03-medical-appointment-template/)
- Gabarito: [`03-medical-appointment-z/`](../../../modulo02-integracao-apis-llms/03-medical-appointment-z/)

Nós em `src/graph/nodes/`. O arquivo `identifyIntentNode.ts` no template **devolve o state quase intacto**. Há um `try/catch` e um log. Não há chamada ao modelo. Seu trabalho é ligar o prompt em `src/prompts/v1/identifyIntent.ts` ao nó, preencher `intent`, e deixar o grafo seguir para `schedulerNode`, `cancellerNode` ou `messageGeneratorNode`. O serviço de domínio é `appointmentService`. Structured output: o modelo não “conversa sobre medicina”; ele **classifica intenção** para um código TypeScript decidir o próximo passo.

Ignore o README “article generator”. Os testes E2E pedem chave real. O checkpoint C02.2 é este template, não um print do `-z`.

No `src/prompts/v1/identifyIntent.ts` o contrato é intenção enumerada, não prosa. No gabarito você vai ver o modelo devolver algo que o TypeScript consegue ligar a `schedulerNode` ou `cancellerNode`. Se a sua implementação colocar a frase inteira do paciente em `intent`, o grafo não ramifica — só “conversa”. O `appointmentService` é o efeito colateral (agendar de verdade). Structured output sem efeito no serviço é demo de chatbot, não o lab.

Abra `src/graph/graph.ts` e `factory.ts` no template **antes** de escrever o nó. O desenho já existe: falta o miolo do identify. Copiar o `-z` inteiro e mudar três strings não demonstra que você leu o StateGraph.

### Memória não é o buffer do chat

[`04-song-highlights-template/`](../../../modulo02-integracao-apis-llms/04-song-highlights-template/) (gabarito `04-song-highlights-z/`) sobe Postgres com `docker compose`. Scripts `chat:erickwendel` e `chat:ana` não são frescura: são **dois usuários**. A conversa é de curto prazo. A preferência (gênero, destaque de música) é de longo prazo e mora no banco.

No M04 U4 o OpsPilot vai ter memória semântica com embeddings. Aqui a lição é mais humilde e mais útil no dia a dia: se a preferência não está numa tabela, o próximo processo “esquece”. LangGraph checkpoint ≠ perfil de produto.

### Papéis, não “o modelo é legal”

[`05-safeguard-prompt-injection-template/`](../../../modulo02-integracao-apis-llms/05-safeguard-prompt-injection-template/) ensina o modelo de ameaça que o M03 (service token) e o M06 (HITL) vão endurecer. CLI com `--user` e `--unsafe`. Scripts `chat:member:safe`, `chat:member:unsafe:env`, `unsafe:package`. Dados em `data/users.json`.

A regra: **nunca** autorize leitura de arquivo com base no texto do usuário. O membro tenta injection e deve ser bloqueado. Um papel privilegiado pode passar no caso de teste — e você precisa **demonstrar os dois**. O template **não** tem pasta `tests/` apesar do README. O `-z` ainda traz `mcpService.ts` (filesystem). Não copie o MCP para “completar” o template se o exercício do guia for o safeguard.

Prompt injection, neste repositório, não é teoria de CTF. É o usuário pedindo para o assistente soltar um `.env`. O guardrail é código, não um parágrafo no system prompt.

### Text-to-Cypher não é o RAG do PDF

No M01 você recuperou trechos do `tensores.pdf`. Agora o LLM **escreve Cypher** contra um grafo de alunos e cursos.

- Template: [`06-rag-neo4j-students-template/`](../../../modulo02-integracao-apis-llms/06-rag-neo4j-students-template/) — siga **[`plan.md`](../../../modulo02-integracao-apis-llms/06-rag-neo4j-students-template/plan.md)**, não o README.
- Gabarito: [`06-rag-neo4j-students-z/`](../../../modulo02-integracao-apis-llms/06-rag-neo4j-students-z/)

Comandos do guia: `npm run docker:infra:*`, `npm run seed`, E2E `tests/sales.e2e.test.ts`. Há um loop de correção: Cypher inválido volta para o modelo. Isso é engenharia — o grafo não “entende português”; ele entende Cypher. Sua entrega: uma pergunta de ranking de curso e o Cypher gerado.

O lab [`07-doc-analysis/`](../../../modulo02-integracao-apis-llms/07-doc-analysis/) é Fastify na **:4000**, upload de PDF. **Não há PDF em `docs/` neste clone** e não há pasta `tests/` apesar dos scripts. Use um PDF seu. É opcional se você já fechou o Cypher (C02.4 pede um dos dois).

---

## Passo a passo

1. **Chave.** `OPENROUTER_API_KEY` no `.env` de cada lab que chama modelo. Sem isso o E2E médico não é “código quebrado”: é chamada recusada.
2. **Router (2.1).** `cd 01-smart-model-router-gateway`, copie `.env.example`, `npm test`, um `curl` em `POST /chat`. Quebre o nome do modelo de propósito.
3. **Intro (2.2).** Sirva o grafo sem LLM. Desenhe no papel: estado inicial, nó, condição, estado final. Três caixas bastam.
4. **Médico (2.3).** No template, implemente `identifyIntentNode` até o intent deixar de ser vazio/unknown no caminho feliz. Rode o E2E. Só então abra o `-z` e escreva o parágrafo “o que o gabarito fez diferente”.
5. **Memória (2.4).** `docker compose` no 04. Converse como Erick, converse como Ana. Confira no Postgres se a preferência sobreviveu ao restart do processo Node.
6. **Safeguard (2.5).** Capture a saída de `chat:member:safe` versus um `unsafe:*`. Uma tela dos dois lados.
7. **Cypher (2.6).** Infra, seed, uma pergunta de ranking. Cole o Cypher. Se o tempo apertar, o 07 com PDF próprio substitui o C02.4 — não os dois obrigatórios.

Projeto do módulo: **uma** API LangGraph (médico **ou** Cypher) a partir do template, README de ~20 linhas (como subir, chave, `curl`), testes verdes, parágrafo do diff com o `-z`.

---

## Armadilhas

- **Seguir o README “article generator”.** Documentado em [`curso/lacunas-e-proximos-passos.md`](../../lacunas-e-proximos-passos.md). O código manda.
- **Entregar o `-z` como se fosse o template.** C02.2 é explícito: medical no template.
- **LangGraph = sempre LLM.** O lab 02 existe para impedir essa frase na prova.
- **Um único usuário no lab 04.** Sem Ana versus Erick você não demonstrou persistência de perfil.
- **Confiar no system prompt contra injection.** O lab 05 pede safeguard de papel. O texto do atacante não é fonte de autorização.
- **Lab 06 pelo README, não pelo `plan.md`.** O plano é a spec.
- **Lab 07: procurar o PDF da aula em `docs/`.** Não está no clone. Traga o seu. Não invente URL de dataset.
- **Achar que Cypher gerado é o mesmo RAG do exemplo 13.** No 13 o modelo lê trechos. No 06 ele escreve consulta. Falhas diferentes (alucinação de cláusula versus trecho errado).

---

## Síntese

Você colocou o LLM atrás de HTTP, de um grafo com estado, de um banco e de um modelo de papéis. Intent estruturado substituiu “o bot entende”. Memória virou tabela. Injection virou caso de teste. Cypher virou ferramenta com loop de correção.

O Módulo 03 vai expor **tools** com o mesmo rigor: o agente não lê o Mongo “porque o prompt mandou”; lê porque o servidor MCP publicou `create`/`list` e, no lab 07, só com `SERVICE_TOKEN`.

---

## Exercício de fixação

Escolha **um** eixo e entregue evidência. Não precisa dos sete labs no zip.

**Opção A — Gateway + médico.** `curl` do `POST /chat` do router (incluindo um modelo inválido) + E2E do template médico verde + o `identifyIntent` preenchido (trecho ou print). Parágrafo: o que o `-z` fez que você não fez.

**Opção B — Safeguard + Cypher.** Output do membro bloqueado e do caso privilegiado + Cypher gerado de uma pergunta de ranking (seed rodado). Uma frase: por que o texto do usuário não autoriza leitura de arquivo.

Em ambos os casos, um README de 20 linhas da API que você escolheu como projeto do módulo.
