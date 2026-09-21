![Capa do Módulo 03 — MCP na prática](../../media/imagens/modulo-03-capa.png)

# Módulo 03 — MCP na prática

Guia: [`curso/modulos/03.md`](../../modulos/03.md). Pasta: [`modulo03-mcp-na-pratica/`](../../../modulo03-mcp-na-pratica/). Carga: ~24 h. Complemento: live [`lives/2026-02-24/`](../../../lives/2026-02-24/) (`base-teorica/mcp-model-context-protocol.md` e os textos de Agent Skills).

READMEs de `customers-mcp` que repetem o texto do CipherSuite: **ignore**. O CipherSuite (AES) está no lab 05. Customers é CRUD de clientes no lab 06.

---

## Abertura

No Módulo 01 você **consumiu** MCP (Playwright, Context7, Grafana). No 02 o agente já tinha tools no processo Node. Agora o contrato sai do seu binário e vira **servidor**: qualquer host — Cursor, Copilot, Inspector, LangGraph — pode descobrir tools, resources e prompts do mesmo jeito.

Três papéis que o checklist exige distinguir:

1. **Servidor MCP** — o processo que declara ferramentas (CipherSuite, customers).
2. **Host** — o IDE ou o agente que conecta (`.vscode/mcp.json`, Copilot Chat).
3. **Inspector** — UI de depuração (`npm run mcp:inspect` no gabarito 05).

Se você tratar os três como “o plugin”, o lab 07 (token) fica incompreensível: quem recusa a chamada é a **API Fastify**; o MCP só repassa o `SERVICE_TOKEN`.

Ao final: um agente LangGraph fala com várias tools; um servidor MCP nasce do zero; uma API legado vira MCP; JWT/RBAC/service token recusam o anônimo; e você publica no Verdaccio **ou** consome via `MultiServerMCPClient`.

A spec oficial está em [modelcontextprotocol.io](https://modelcontextprotocol.io/) — link já no README da raiz e no syllabus. Três primitivas bastam para esta semana:

- **Tool** — função com schema JSON. O modelo escolhe chamar. CipherSuite: `encrypt_message`. Customers: `create`/`list`.
- **Resource** — dado para o host ler (`encryption://info` descreve AES, derivação de chave, formato `IV:ciphertext`). Não é uma ação; é contexto.
- **Prompt** — modelo de conversa pronto (`encrypt_message_prompt`). O host oferece ao usuário; não substitui o system prompt do seu agente LangGraph.

Transporte, neste material, é sobretudo o processo local que o Inspector e o `.vscode/mcp.json` disparam. Não invente um gateway HTTP se o lab sobe via stdio.

---

## Conceitos (neste clone)

### Tool não é “o modelo acessa a internet”

Em [`01-multiple-mcp-tools-template/`](../../../modulo03-mcp-na-pratica/01-multiple-mcp-tools-template/) a função `getMCPTools()` **devolve array vazio**. O gabarito [`01-multiple-mcp-tools-z/`](../../../modulo03-mcp-na-pratica/01-multiple-mcp-tools-z/) liga `fsTool`, `mongodbTool` e escreve `reports/`. Há `docker-compose.yaml` (Mongo + Express). O `package.json` pode mencionar SerpAPI: o código é **vendas em `data/sales.csv`**. Pergunta honesta de lab: “quais os top produtos?”. Se o agente responder sem tool, você não ligou o MCP — só o chat.

[`02-google-trends-agent/`](../../../modulo03-mcp-na-pratica/02-google-trends-agent/) é o lab que **de fato** usa SerpAPI (`SERPAPI_API_KEY`), Fastify `/chat`, tool `google_trends`. README interno errado. Scripts de teste sem pasta `tests/` visível. **Opcional** se não houver chave — o guia autoriza pular.

### Instructions e Skills não são servidor MCP

[`03-dev-instructions-agents/`](../../../modulo03-mcp-na-pratica/03-dev-instructions-agents/) é `.github/agents/*.agent.md`. Copie para o seu IDE. Sem `npm`. É o jeito de **falar com o host**: personalidade, limites, pasta permitida. No M04 U1 a Notas API vive disso.

[`04-skills/`](../../../modulo03-mcp-na-pratica/04-skills/) traz `.agents/skills/`, `refs.txt` e demos. Junte com a live 2026-02-24 (`agent-skills-*.md`). Skill é procedimento empacotado para o agente; MCP é protocolo de ferramentas. Os dois se complementam. Nenhum substitui autenticação.

### MCP do zero: tools, resource, prompt

[`05-mcps-do-zero-template/`](../../../modulo03-mcp-na-pratica/05-mcps-do-zero-template/) é crypto local **sem** MCP. O gabarito [`05-mcps-do-zero-z/`](../../../modulo03-mcp-na-pratica/05-mcps-do-zero-z/) é o **CipherSuite**: README **correto**. `src/mcp.ts` expõe:

- tools `encrypt_message` e `decrypt_message` (AES-256-CBC, scrypt, saída `IV:ciphertext` em hex);
- resource `encryption://info`;
- prompts prontos para o host.

`.vscode/mcp.json` liga o servidor no VS Code. `npm run mcp:inspect` abre o Inspector. C03.1 aceita este Inspector **ou** o CRUD de customers. O template existe para você implementar `list_tools` visível — não para copiar o `-z` no primeiro `ls`.

Um teste mental útil no Inspector: criptografe `"aula-03"` com uma passphrase, copie o hex, descriptografe com a **mesma** passphrase, depois tente outra. O IV novo a cada encrypt (README do CipherSuite) faz duas cifras da mesma frase parecerem diferentes. Se o seu servidor devolver sempre o mesmo blob, você fixou o IV — e a aula de crypto falhou junto com a de MCP.

### API legado como MCP

[`06-your-legacy-api-as-mcp/`](../../../modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/) é o caso de ouro da disciplina:

| Subpasta | Papel |
| --- | --- |
| [`nodejs-fastify-mongodb-crud/`](../../../modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/nodejs-fastify-mongodb-crud/) | API HTTP **:9999** + Docker Mongo |
| [`customers-mcp-template/`](../../../modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/customers-mcp-template/) | `McpServer` vazio |
| [`customers-mcp-z/`](../../../modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/customers-mcp-z/) | tools CRUD |

Suba a API **antes** do MCP. Crie um cliente via tool e confira no Mongo Express. A lição de arquitetura: você não reescreve o legado em “agente”. Você **embrulha** o que já tem. O TrialForge (M08) vai chamar isso de ferramenta de domínio atrás do orquestrador.

### Auth: o token não mora no prompt

[`07-api-security-auth-rate-limiting-template/`](../../../modulo03-mcp-na-pratica/07-api-security-auth-rate-limiting-template/) versus [`07-api-security-auth-rate-limiting-z/`](../../../modulo03-mcp-na-pratica/07-api-security-auth-rate-limiting-z/). Cada lado tem `nodejs-fastify-mongodb-crud-z/` e `customers-mcp-z/`. O nome `-z` **dentro do template** é armadilha documentada no guia: compare a **API do template** com a **API da pasta `07-…-z`**.

O que o gabarito acrescenta: JWT, `requireRole`, `POST /v1/auth/service-token`. O MCP chama `getServiceToken.sh` e envia `SERVICE_TOKEN`. Sem token, a API recusa. Com token, o CRUD passa. Isso é C03.2. Rate limit é o irmão chato que impede o agente de martelar o Mongo.

### Publicar e consumir

[`08-publishing-mcps-private-npm/`](../../../modulo03-mcp-na-pratica/08-publishing-mcps-private-npm/) — só gabarito. Verdaccio na **:4873** (`customers-mcp-z/docker-compose.yaml`). Scripts `registry:*`, `release:private`. Registry privado é o anti-padrão “colei o `mcp.ts` em dez repositórios”.

[`09-using-mcp-with-langchain/`](../../../modulo03-mcp-na-pratica/09-using-mcp-with-langchain/) — também só `-z`. `MultiServerMCPClient` + API no ar + `SERVICE_TOKEN` + OpenRouter. Fecha o ciclo: o grafo do M02 agora **descobre** tools MCP em vez de importar funções locais.

C03.3: Verdaccio **ou** Trends **ou** lab 09. Não os três.

---

## Passo a passo

1. Leia a live `mcp-model-context-protocol.md` (mesmo que por cima). Vocabulário: tool, resource, prompt, stdio/HTTP.
2. Lab 01: faça o template devolver **pelo menos uma** tool e responder “top produtos” do CSV. Docker do Mongo ligado.
3. Labs 03–04: copie uma instruction e abra uma skill. Sem npm. Anote a diferença em uma frase.
4. Lab 05: no template, exponha tools no Inspector. Conferir com o README do CipherSuite no `-z` **depois**.
5. Lab 06: API `:9999` no ar → MCP → `create` → documento no Mongo Express.
6. Lab 07: uma chamada MCP sem token (falha) e com token (ok). Guarde o `curl` do token. **Não** cole o valor da chave no PDF da entrega.
7. Desafio: 08 **ou** 09.

Antes de chamar o lab fechado, faça o Inspector listar tools **sem** o modelo no meio. Se `encrypt_message` não aparece, o host está certo e o servidor não. Se aparece e o agente “não consegue criptografar”, o problema é schema ou passphrase — outro diagnóstico. Esse hábito (separar host, servidor e modelo) é o que o C03 pede na frase de vocabulário.

Projeto do módulo: **Customers MCP autenticado** — API do lab 07 (template evoluído) + MCP que só opera com service token. Entrega: `curl` do endpoint de token (mascarado), log do Inspector ou do cliente, e o que acontece se o token expira ou falta.

---

## Armadilhas

- **README do customers copiado do CipherSuite.** Criptografia AES não cria cliente. Olhe `src/` e o guia.
- **`getMCPTools()` vazio e achar que o CSV “já entra no contexto”.** Sem tool, o modelo chuta.
- **Subir o MCP antes da API no lab 06.** Connection refused não é bug de schema de tool.
- **Subpastas `*-z` no template 07.** Compare pastas irmãs `07-…-template` versus `07-…-z` no nível de cima.
- **Colocar JWT no system prompt.** O lab 07 recusa na API. O modelo não é o enforcement.
- **SERPAPI como bloqueio do módulo.** Lab 02 é opcional.
- **Publicar no npm público “para testar”.** O exercício é Verdaccio local `:4873`.
- **Node do CipherSuite.** O README do 05-z cita engine v24+; o restante da pós pede Node 22. Se o Inspector falhar por engine, documente a versão — não invente outro servidor.

---

## Síntese

MCP é o USB-C das ferramentas de agente: o host não precisa de um SDK por banco. Você viu o contrato dos dois lados — consumidor (lab 01, 09) e produtor (05, 06) — e descobriu que produção começa no token, não no `list_tools` bonito.

Uma analogia de engenharia de software clássica: o servidor MCP é a sua API; o host é o cliente HTTP; o Inspector é o Postman; o modelo é só quem **escolhe** qual rota chamar. Ninguém autoriza um `DELETE` porque o JSON de body “pediu com educação”. O lab 07 existe para essa analogia doer. Se o seu caderno ainda diz “o Copilot acessa o Mongo”, reescreva: o Copilot acessa o **host**, o host chama o **MCP**, o MCP chama a **API**, a API exige **token**. Quatro hops. Um pulo a menos e você está de volta no prompt injection do M02.

O OpsPilot, no M04 U3, vai expor **ele mesmo** como servidor MCP (`npm run mcp`). A ideia é esta aula. A diferença é o domínio: incidente do Mercadinho em vez de AES e customers.

---

## Exercício de fixação

Três evidências, uma página:

1. **Inspector ou CRUD.** Print ou log de `list_tools` do CipherSuite **ou** um `create` de customer refletido no Mongo.
2. **Token.** Chamada MCP sem `SERVICE_TOKEN` (erro) e com token (sucesso). Mascarar o segredo.
3. **Uma frase de vocabulário.** “O host é ___; o servidor MCP é ___; quem autentica o CRUD é ___.”

Se sobrar fôlego, acrescente Verdaccio ou o `/chat` do lab 09. C03.3 agradece. Não é obrigatório para entender o módulo.
