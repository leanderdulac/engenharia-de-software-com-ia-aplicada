# Lab 01 — Smart model router (gateway)

Gateway Fastify `POST /chat` que escolhe modelo/provider no **OpenRouter** (`src/server.ts`, `src/openrouterService.ts`).
Não há pasta `*-template` / `*-z`: é projeto único.

Guia do módulo: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.1.

## Disco

- `.env.example` → `OPENROUTER_API_KEY`
- Testes: `tests/router.e2e.test.ts` — **chamam a API real**. Sem chave = bloqueado.
- Sem README antigo (este ficheiro).

## Comandos

```bash
cp .env.example .env   # cole a chave; não commite
npm ci
npm test               # E2E OpenRouter (pago/quota)
npm run dev
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).


**Não é** gerador de artigos. Checkpoint C02.1 aceita este lab **ou** o lab 02 (LangGraph sem LLM).
