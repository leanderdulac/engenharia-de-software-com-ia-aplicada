# Lab 07 gabarito — Auth / rate limit / service token

API com JWT/RBAC/service token + MCP que só opera com `SERVICE_TOKEN`.

```bash
cd nodejs-fastify-mongodb-crud-z && npm ci && npm run infra:up && npm start
cd ../customers-mcp-z
# getServiceToken.sh fala com :9999 — mascare a saída
npm ci
SERVICE_TOKEN=… npm run mcp:inspect
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
