# Lab 02 — Google Trends (SerpAPI)

Único lab deste módulo que usa **`SERPAPI_API_KEY`**. Tool `google_trends` + Fastify `/chat`. Sem pasta `tests/`.

Guia: [`curso/modulos/03.md`](../../curso/modulos/03.md) § 3.2. **Opcional** se não houver chave (C03.3).

`package.json` declara `test` / `test:e2e` mas **não há pasta `tests/`** neste clone. Avalie pelo `/chat`.

```bash
cp .env.example .env   # SERPAPI_API_KEY + OPENROUTER_API_KEY
npm ci
npm run dev
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
