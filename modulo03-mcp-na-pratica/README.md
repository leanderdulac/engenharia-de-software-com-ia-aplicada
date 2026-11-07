# Módulo 03 — labs

Guia oficial: [`curso/modulos/03.md`](../curso/modulos/03.md).

READMEs das pastas descrevem o que está no disco (CSV de vendas ≠ SerpAPI; customers MCP ≠ CipherSuite).

## Inspector e Node (fontes oficiais, 7 nov. 2026)

Comando: `npx @modelcontextprotocol/inspector` (ou o script `npm run mcp:inspect` do lab).
UI web: `CLIENT_PORT` default **6274** ([variáveis de ambiente](https://github.com/modelcontextprotocol/inspector/blob/main/docs/environment-variables.md)). **Não** é 5173 (Vite antigo / v1).

- Site MCP: Node **≥ 22.19.0** ([docs/tools/inspector](https://modelcontextprotocol.io/docs/tools/inspector)).
- Pacote npm `@modelcontextprotocol/inspector` **2.14.0** `engines`: `^22.23.4 || ^24.22.1 || >=26.12.1` ([package.json](https://github.com/modelcontextprotocol/inspector/blob/main/package.json)).
- CipherSuite/customers MCP neste clone: `engines.node` = `v24.14.0` (não alterado).
- Isolamento neste clone: trilha/preview **22.23.4**; Inspector e labs M03 **24.22.1** (`.nvmrc` no CipherSuite). `npm` avisa EBADENGINE no 24.22.1 vs `v24.14.0` exacto — os testes MCP mesmo assim passam.

Handshake CLI (sem UI): `npx @modelcontextprotocol/inspector@2.14.0 --cli node --experimental-strip-types src/index.ts --method tools/list`.

CipherSuite gabarito (`05-mcps-do-zero-z`): `npm run mcp:inspect` = `npx @modelcontextprotocol/inspector node src/index.ts`.

Mongo local: `HOST=127.0.0.1 PORT=9999 DB_NAME=customers npm start` no CRUD (bind `0.0.0.0` só se `HOST` for passado, p.ex. Render). Verdaccio `127.0.0.1:4873` se o daemon Docker estiver a correr. SerpAPI continua a precisar de chave. UI Inspector na porta 6274 **não** faz parte do smoke CLI.
