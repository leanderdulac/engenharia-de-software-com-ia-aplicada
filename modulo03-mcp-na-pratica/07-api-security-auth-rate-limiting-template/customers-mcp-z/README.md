# Customers MCP

Servidor MCP que embrulha a API de customers (`POST/GET/PATCH/DELETE` em `:9999`).
**Não é** `@erickwendel/ciphersuite-mcp`. O README anterior era cópia desse lab.

## Tools (gabarito)

`list_customers`, `create_customer`, `get_customer`, `update_customer`, `delete_customer`.

## Comandos

Suba a API Fastify+Mongo **primeiro**. Depois:

```bash
npm ci
npm start
npm run mcp:inspect
npm test    # se existir pasta tests/ nesta cópia
```

```bash
npm run mcp:inspect
# equivale a: npx @modelcontextprotocol/inspector node src/index.ts
```

Pacote oficial: `@modelcontextprotocol/inspector`. UI web na **porta 6274** (`CLIENT_PORT` default v2).
Fontes e engines: [README do módulo 03](../../README.md). READMEs antigos com `:5173` estão desatualizados.


Labs 07+: exporte `SERVICE_TOKEN` (script `getServiceToken.sh` no gabarito 07). Não cole o token no Git.

`package.json` `engines.node`: `v24.14.0`. Inspector/Node: ver [README do módulo](../../README.md).


Esta cópia está **dentro do template 07**. O sufixo `-z` no nome da pasta é armadilha: compare a API desta pasta com a da pasta `07-…-z`.
