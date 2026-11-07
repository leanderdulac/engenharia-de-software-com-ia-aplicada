# Lab 06 — API legado como MCP

Três subpastas. Suba a **API antes** do MCP.

| Subpasta | Papel | Porta |
| --- | --- | --- |
| `nodejs-fastify-mongodb-crud/` | API Fastify + Docker Mongo | `:9999` |
| `customers-mcp-template/` | `McpServer` vazio | stdio |
| `customers-mcp-z/` | tools CRUD | stdio |

O README dentro de `customers-mcp-*` **não** é CipherSuite. Tools do gabarito:
`list_customers`, `create_customer`, `get_customer`, `update_customer`, `delete_customer`.

```bash
cd nodejs-fastify-mongodb-crud && npm ci && npm run docker:infra:up && npm start
cd ../customers-mcp-z && npm ci && npm run mcp:inspect
```

API `engines`: `v20.11.0`. MCP `engines`: `v24.14.0`. Trilha: Node 22. Teste e documente.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
