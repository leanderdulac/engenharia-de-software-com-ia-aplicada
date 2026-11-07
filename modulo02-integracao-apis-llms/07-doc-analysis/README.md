# Lab 07 — Doc analysis (PDF Q&A)

Fastify em **`:4000`**, `POST /chat` (multipart: ficheiro PDF + campo `question`).
Há PDF de exemplo no disco: [`docs/a-comprehensive-overview-of-large-language-models.pdf`](./docs/a-comprehensive-overview-of-large-language-models.pdf) (~434K).
Survey: https://arxiv.org/pdf/2307.06435

**Não há pasta `tests/`** apesar de `package.json` declarar `npm test` / `test:dev`.
`src/index.ts` ao arrancar pode enviar o PDF de exemplo ao grafo (**chamada OpenRouter**). Não rode `npm start` neste smoke.

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.7. C02.4 aceita Cypher (lab 06) **ou** PDF neste lab.

```bash
cp .env.example .env
npm ci
npm run dev    # bloqueado sem chave; bind 0.0.0.0:4000
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).
