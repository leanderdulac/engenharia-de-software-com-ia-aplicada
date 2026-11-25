# Lab 02 — LangGraph intro (sem LLM)

StateGraph que classifica `upper` / `lower` **por palavra-chave** (`identifyIntentNode.ts`).
Não chama OpenRouter. Serve para C02.1 sem chave.

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.2.

## Disco

- `.env.example` só tem LangSmith (opcional). `npm test` **não** lê `.env`.
- Testes: `tests/router.e2e.test.ts` (nome herdado) — inject Fastify, 3 casos, sem API.

## Comandos

```bash
npm ci
npm test
npm run langgraph:serve   # opcional
npm run dev
```

`POST /chat` com `{ "question": "make this UPPER please" }`.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).
