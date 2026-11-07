# Lab 04 — Song highlights + memória

Chat LangGraph que persiste **preferências** em **Postgres** (não LibSQL).
`docker-compose.yml` sobe `postgres` na `:5432`; `src/config.ts` usa
`postgresql://postgres:mysecretpassword@localhost:5432/song_recommender`.

README antigo falava MemorySaver/LibSQL e ficheiro de testes que **não** está no disco.
Teste real: `tests/chat.e2e.test.ts` (API OpenRouter).

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.4. Formativo — não há C02.x.

## Comandos

```bash
cp .env.example .env
npm ci
npm run docker:up
npm run chat:erickwendel
npm run chat:ana
npm test                 # E2E com chave
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).
