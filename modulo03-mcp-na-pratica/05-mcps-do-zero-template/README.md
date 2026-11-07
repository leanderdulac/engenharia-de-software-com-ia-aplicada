# Lab 05 template — crypto local, **ainda sem MCP**

`src/index.ts` + `src/service.ts`: `encrypt` / `decrypt` AES na CLI.
**Não** há `src/mcp.ts` nesta pasta. O README CipherSuite completo pertence ao **gabarito** `-z`.

```bash
npm ci
node src/index.ts
```

Depois implemente o servidor MCP (tools `encrypt_message` / `decrypt_message`, resource, prompts)
como no gabarito `05-mcps-do-zero-z/`. C03.1: Inspector **ou** customers CRUD.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
