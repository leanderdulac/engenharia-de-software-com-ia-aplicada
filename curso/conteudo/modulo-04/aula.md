![Capa do Módulo 04 — Agentes autônomos](../../media/imagens/modulo-04-capa.png)

# Módulo 04 — Criação de agentes autônomos

Guia: [`curso/modulos/04.md`](../../modulos/04.md). Pasta: [`modulo04-criacao-de-agentes-autonomos-novo/`](../../../modulo04-criacao-de-agentes-autonomos-novo/) — leia o [`README.md`](../../../modulo04-criacao-de-agentes-autonomos-novo/README.md) **e** o `UNIDADE.md` de cada snapshot. Carga: ~36 h. Live SDD: [`lives/2026-05-27/`](../../../lives/2026-05-27/).

A pasta antiga `modulo04-agentes-autonomos/` **não está neste clone**. Planos `unidade-N-plano-de-aula.html` também não. O que vale é o snapshot + `UNIDADE.md` (incluindo a seção “o que o roteiro planejou e não entrou”).

---

## Abertura

Dois produtos, uma disciplina.

A **Unidade 1** não é o OpsPilot. É a [`notas-api/`](../../../modulo04-criacao-de-agentes-autonomos-novo/01-arquitetura-de-agentes-de-codigo/notas-api/), um CRUD/CLI de tarefas para você **operar o agente de código** com método: instructions, permissões de terminal, spec → plano → tarefas → implementação. Se pular a U1, as unidades 2–9 viram “rode o `npm run dev` e admire”. A pós quer o contrário: você manda no agente, o agente não manda no Git.

Das unidades 2 a 9 o caso é o **OpsPilot**, copiloto de plantão do e-commerce fictício **Mercadinho**. Um único projeto. Cada pasta é o estado **ao final** da unidade. Não misture `src/` da U3 com `web/` da U8. Specs numeradas em `specs/NNN-slug/` (Spec Kit). Modelos via OpenRouter; `:free` no README do módulo.

Ao final você compara ReAct, Plan-and-Execute e Reflection com métrica no **store** (não no texto bonito); expõe tools e o próprio OpsPilot como MCP; persiste conversa e memória semântica; orça contexto; roda o grafo de produção com roteador; liga HITL (HTTP 202); publica a war room; e dispara o modo **team**.

---

## Conceitos (unidade a unidade, no disco)

### U1 — O agente de código é um colega com guardrail

Pasta: [`01-arquitetura-de-agentes-de-codigo/`](../../../modulo04-criacao-de-agentes-autonomos-novo/01-arquitetura-de-agentes-de-codigo/). Specs em `notas-api/specs/`. Fluxo `/especificar` → `/planejar` → `/tarefas` → `/implementar` (os nomes exatos do seu IDE podem ser os do Spec Kit). Instructions em `.github/`.

A regra da aula: uma feature nova **não** começa com você editando `src/` na mão. Começa com spec. O agente implementa. Você revisa o diff. Terminal com permissão estreita. Live 2026-05-27 mostra o mesmo gesto em outro recorte.

Isso é SDD — Spec-Driven Development. O glossário do curso aponta para cá. No M05 o CFP usa OpenSpec; é primo, outro formato.

### U2 — Três estratégias, uma métrica honesta

[`02-padroes-de-raciocinio-e-execucao/`](../../../modulo04-criacao-de-agentes-autonomos-novo/02-padroes-de-raciocinio-e-execucao/). Specs `001-reasoning-nucleus` e `002-reflection-layer`.

- `src/strategies/react.ts` — Thought → Action → Observation (paper Yao et al., arXiv `2210.03629`, já no README da raiz / syllabus).
- `src/strategies/plan-execute.ts` — planeja, executa, replaneja.
- `src/strategies/reflect.ts` — crítico com teto de iterações.

Tools ainda são mock sobre `in-memory-store` (`list_alerts`, `open_incident`, `resolve_incident`) com seed do Mercadinho. O `npm run bench` mede acerto no **estado do store**, não no parágrafo que o modelo escreveu. `npm run arena -- --strategies react,plan-execute` coloca os dois lado a lado. Trace tipado em `src/trace/builder.ts`.

Se faltar `.env.example` nesta pasta (lacuna documentada em U2–U5), copie o de [`06-langgraph-e-workflows-complexos/`](../../../modulo04-criacao-de-agentes-autonomos-novo/06-langgraph-e-workflows-complexos/).

O `POST /chat` **não** está neste snapshot — o `UNIDADE.md` avisa: foi para a U3.

### U3 — Tools de verdade e o OpsPilot como MCP

[`03-function-calling-e-tool-use/`](../../../modulo04-criacao-de-agentes-autonomos-novo/03-function-calling-e-tool-use/). Specs 003–006. `POST /chat`, SQLite (`004-sqlite-ops-store`), tool de status de provider, `npm run mcp` (`006-mcp-ops-server`).

Aqui o M03 encontra o produto: o incidente deixa de ser mock puro e o servidor MCP é o próprio copiloto. Registre uma tool sua — mesmo stub — e mostre a chamada no trace. C04.3 é `/chat` + tool.

### U4 — Memória que não é o log do terminal

[`04-memoria-e-reflexao-em-agentes-autonomos/`](../../../modulo04-criacao-de-agentes-autonomos-novo/04-memoria-e-reflexao-em-agentes-autonomos/). Specs 007–009. `/chat` com `conversationId` e `userId`. `POST /memories`. Evento `learning`. Embeddings Hugging Face na primeira run (rede). Reflexão deixa de ser só estratégia U2 e vira aprendizado persistido.

Compare com o lab 04 do M02 (Postgres de preferência musical): lá era perfil tabular. Aqui é recall semântico. Os dois existem em produção. Não substitua um pelo outro no discurso.

### U5 — Contexto é orçamento

[`05-gerenciamento-de-contextos/`](../../../modulo04-criacao-de-agentes-autonomos-novo/05-gerenciamento-de-contextos/). Specs 010–012. Script `./scripts/conversa-longa.sh` (30 turnos). Eventos `context` e `summarize`. O ContextBuilder monta o prompt **por seção** com teto de tokens. Sem isso, a conversa longa estoura a janela ou some o runbook no meio do ruído.

### U6 — Grafo de produção, sem `strategy` na porta

[`06-langgraph-e-workflows-complexos/`](../../../modulo04-criacao-de-agentes-autonomos-novo/06-langgraph-e-workflows-complexos/). Specs 013–014. `POST /chat` **sem** campo `strategy` → o grafo escolhe (`route` / `routeReason`) e há fallback de modelo. Ainda **não** há `web/`. Quem abre a U8 achando que a UI nasceu junto com o roteador está misturando snapshots.

### U7 — Observar e frear

[`07-observabilidade-e-limites-de-autonomia/`](../../../modulo04-criacao-de-agentes-autonomos-novo/07-observabilidade-e-limites-de-autonomia/). Spec 015.

Leia o `UNIDADE.md` com atenção: o roteiro planejou `interrupt()` do LangGraph no meio de uma tool `silence_all_alerts`. **Não entrou.** O que existe: flag `awaitHumanApproval: true` no request → HTTP **202** com `approvalId` e resumo; `POST /approvals/:id` com `{approve: true}` executa o que ficou pendente. Logger em `src/obs/logger.ts` registra **metadados, nunca conteúdo** (a regra virou teste — PII). `GET /requests/:id` e `GET /stats` (agregados; **sem** custo em dólares, também desvio documentado).

HITL daqui é o mesmo espírito da senha `GESTOR-APROVA` no Nexus e do Approval Gate do TrialForge. Três produtos, um princípio: ação destrutiva não é autônoma por default.

### U8 e U9 — War room e time

[`08-projeto-pratico-opspilot-publicado/`](../../../modulo04-criacao-de-agentes-autonomos-novo/08-projeto-pratico-opspilot-publicado/). Specs 016–017. API **:3000** + `web/` **:5173**. README da pasta fala em Pages. `.github/workflows/deploy.yml`. A UI de aprovar/negar mora aqui.

[`09-multi-agent-systems/`](../../../modulo04-criacao-de-agentes-autonomos-novo/09-multi-agent-systems/). Spec 018, `src/team/`. Pedidos que exigem análise + plano + ação → rota `team`, eventos `handoff`, blackboard. Supervisor despacha papéis. O M08 lista seis padrões de orquestração; aqui você **vê um** funcionando no Mercadinho.

Comandos padrão U2–U9: `npm ci`, `cp .env.example .env`, `npm run dev`, `npm test`, `npm run typecheck`. Testes com fakes — não queimam cota. Modelos `:free` no OpenRouter existem para a demo; o README do módulo aponta o filtro `max_price=0`. Não troque para um modelo pago no meio da arena “para ficar mais inteligente”: você quebra a comparação entre estratégias.

Como ler um snapshot na prática: abra **só** o `UNIDADE.md` da pasta em que está. Ele lista specs novas, arquivos-chave e desvios. Depois `specs/NNN-slug/`. Só então `src/`. Se começar pelo `src/` da U9, você não sabe o que nasceu na U5 (orçamento) versus o que nasceu na U7 (202). O instrutor avalia o discurso da unidade, não o `node_modules` mais gordo.

---

## Passo a passo

Não tente “o OpsPilot completo” no primeiro fim de semana. O guia já fatia ~4 h por unidade.

1. **U1.** Clone mental: você é a pessoa engenheira, o Copilot é o estagiário rápido. Uma feature só via spec. Diff no Git. Live SDD se travar no ritual.
2. **U2.** Arena ReAct versus Plan-and-Execute. Tabela de acertos. Uma frase: em qual cenário o plano inteiro ajuda e em qual o passo a passo ReAct se sai melhor **neste** seed.
3. **U3.** `npm run dev` + um `POST /chat` + `npm run mcp`. Tool no trace.
4. **U4 ou U5.** Ou memória/learning, ou `conversa-longa.sh` com evento `summarize`. C04.4 pede conversa longa **ou** HITL (U7) — não tudo.
5. **U6.** Chat sem `strategy`. Leia `routeReason`.
6. **U7.** `awaitHumanApproval: true` → 202 → aprove → `GET /stats`. Confira que o log não carrega o texto do incidente.
7. **U8 ou U9.** Print da war room (raciocínio visível) **ou** um handoff do modo team.

Projeto do módulo: snapshot **U8 ou U9**, incidente fictício do Mercadinho, trace ou print, e um parágrafo: o que **não** deveria ser autônomo, amarrado ao HITL da U7.

---

## Armadilhas

- **Misturar snapshots.** Copiar `web/` da U8 para a pasta da U6 quebra o discurso da unidade e o `UNIDADE.md`.
- **Ignorar a seção de desvios.** Budget em dólares, `silence_all_alerts`, `interrupt()`: planejados, **ausentes**. Não invente na demo.
- **Julgar estratégia pelo texto do modelo.** O bench usa o store. Um ReAct tagarela que não resolve o incidente perde.
- **U1 editando `src/` primeiro.** O ponto da unidade some.
- **Primeira run da U4 sem rede.** Download de embeddings. Não é “modelo quebrado”.
- **`.env.example` sumido em U2–U5.** Copie da U6. Não commite a chave.
- **Abrir a pasta antiga `modulo04-agentes-autonomos/`.** Ela não existe neste Git.
- **War room na U6.** Não há `web/` ainda.

---

## Síntese

Você treinou o gesto de mandar no agente de código (U1) e depois construiu um agente de **domínio** com as peças da trilha: estratégias (M01/paper ReAct), tools e MCP (M02–M03), memória e contexto, grafo de produção, freio humano, UI, multiagente.

A frase para o M06 e o M08: autonomia é um **slider**, não um boolean. O 202 com `approvalId` é o desenho honesto. O Manager do Nexus e o Approval Gate do TrialForge são o mesmo slider com outra pele.

Se a demo da war room mostrar raciocínio e **não** mostrar o botão de aprovar, você está no snapshot da U8 com um chat que não mandou `awaitHumanApproval`. O contrário também engana: um 202 sem UI (U7) ainda é HITL — só não é “produto publicado”. Escreva no caderno qual snapshot rodou. O avaliador lê o `UNIDADE.md` junto com o seu print. Specs 001 a 018 existem para você citar o número, não para decorar o nome em inglês na prova.

Não existe atalho “pulo da U2 para a U9”. Sem orçamento de contexto (U5) o team mode alucina histórico. Sem tools (U3) o supervisor não tem mãos. A cumulatividade dos snapshots é a pedagogia.

---

## Exercício de fixação

Entregue um dossiê curto do Mercadinho:

1. Tabela da arena (U2) **ou** print do bench — acerto no store.
2. Um `POST /chat` (U3+) com tool visível no trace.
3. Evidência de limite: sumarização da conversa longa **ou** 202 + aprovação.
4. Print da war room **ou** evento `handoff`.
5. Parágrafo HITL: uma ação que o OpsPilot **não** executaria sozinho em produção, e por quê.

Cite o `UNIDADE.md` do snapshot que você rodou. Se o arquivo lista um desvio, não finja que a feature está lá.
