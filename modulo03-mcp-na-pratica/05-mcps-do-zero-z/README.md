# Lab 05 gabarito — CipherSuite MCP

Servidor MCP AES-256-CBC: tools `encrypt_message` / `decrypt_message`,
resource `encryption://info`, prompts. Código em `src/mcp.ts` (no gabarito).
IV novo a cada encrypt. Engine no `package.json`: **`v24.14.0`**.

## Inspector (oficial)

```bash
npm run mcp:inspect
# equivale a: npx @modelcontextprotocol/inspector node src/index.ts
```

Pacote oficial: `@modelcontextprotocol/inspector`. UI web na **porta 6274** (`CLIENT_PORT` default v2).
Fontes e engines: [README do módulo 03](../README.md). READMEs antigos com `:5173` estão desatualizados.


```bash
npm ci
npm test                 # tests/mcp.test.ts existe neste -z
npm run mcp:inspect
```

VS Code: `.vscode/mcp.json`. C03.1 aceita este Inspector **ou** o CRUD de customers (lab 06).

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
