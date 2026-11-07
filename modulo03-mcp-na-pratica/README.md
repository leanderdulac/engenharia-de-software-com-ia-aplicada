# Módulo 03 — labs

Guia oficial: [`curso/modulos/03.md`](../curso/modulos/03.md).

READMEs das pastas descrevem o que está no disco (CSV de vendas ≠ SerpAPI; customers MCP ≠ CipherSuite).

## Inspector e Node (fontes oficiais, 7 nov. 2026)

Comando: `npx @modelcontextprotocol/inspector` (ou o script `npm run mcp:inspect` do lab).
UI web: `CLIENT_PORT` default **6274** ([variáveis de ambiente](https://github.com/modelcontextprotocol/inspector/blob/main/docs/environment-variables.md)). **Não** é 5173 (Vite antigo / v1).

- Site MCP: Node **≥ 22.19.0** ([docs/tools/inspector](https://modelcontextprotocol.io/docs/tools/inspector)).
- Pacote npm `@modelcontextprotocol/inspector` **2.14.0** `engines`: `^22.23.4 || ^24.22.1 || >=26.12.1` ([package.json](https://github.com/modelcontextprotocol/inspector/blob/main/package.json)).
- CipherSuite/customers MCP neste clone: `engines.node` = `v24.14.0`.
- Trilha da pós: Node **22**. Esta VM: **v22.23.4**.

Conflito possível: Node 24.14.0 passa no lab e pode falhar no Inspector; 22.23.4 passa no Inspector e pode avisar no lab. Documente a versão — não troque o servidor. **Inspector não foi aberto nesta VM** (precisa do processo MCP + browser).

CipherSuite gabarito (`05-mcps-do-zero-z`): `npm run mcp:inspect` = `npx @modelcontextprotocol/inspector node src/index.ts`.

Mongo/Verdaccio/SerpAPI = **bloqueados** sem Docker ou chave.
