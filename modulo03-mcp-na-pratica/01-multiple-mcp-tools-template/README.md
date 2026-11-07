# Lab 01 — Múltiplas tools MCP (CSV de vendas)

Agente LangGraph com tools **FS, Mongo e CSV** sobre `data/sales.csv` (gabarito).
A `description` do `package.json` foi alinhada a FS/Mongo/CSV; o lab 02 é que usa SerpAPI/Trends.

Guia: [`curso/modulos/03.md`](../../curso/modulos/03.md) § 3.1.

## Template vs gabarito

| Pasta | Papel |
| --- | --- |
| `01-multiple-mcp-tools-template/` | `getMCPTools()` devolve `[]` — implemente pelo menos uma tool |
| `01-multiple-mcp-tools-z/` | `fsTool`, `mongodbTool`, CSV |

## Comandos

```bash
cp .env.example .env   # OPENROUTER_API_KEY; LangSmith opcional
npm ci
npm run docker:infra:up    # Mongo — bloqueado sem Docker
npm run langgraph:serve
```

Sem pasta `tests/`. Sem SerpAPI neste lab (Trends é o lab 02).

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab.

Inspector: ver o [README do módulo](../README.md) (comando oficial, porta 6274, engines npm vs site).
