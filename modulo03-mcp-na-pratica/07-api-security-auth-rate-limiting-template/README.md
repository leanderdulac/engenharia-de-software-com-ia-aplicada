# Lab 07 template — Auth / rate limit / service token

Duas subpastas, **ambas** com sufixo `-z` no nome (armadilha):

- `nodejs-fastify-mongodb-crud-z/` — API (compare com a pasta `07-…-z`)
- `customers-mcp-z/` — MCP que deve recusar sem `SERVICE_TOKEN`

A API do gabarito 07 acrescenta JWT, `requireRole`, `POST /v1/auth/service-token`.
Script de token: `customers-mcp-z/getServiceToken.sh` no **gabarito** `07-api-security-auth-rate-limiting-z/`.

C03.2: uma chamada MCP sem token (falha) e com token (ok). Mascarar o valor.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
