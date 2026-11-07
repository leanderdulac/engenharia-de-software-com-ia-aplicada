# Lab 06 — RAG Neo4j (alunos/cursos)

Text-to-Cypher contra Neo4j com seed de cursos. **Não** é o RAG de PDF do M01.
**Não** é gerador de artigos (README antigo).

Siga **[`plan.md`](./plan.md)** no template. O plano cita Vercel AI SDK / skills.sh —
confira o que **já está implementado** em `src/` antes de instalar extra.

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.6.

## Disco

- Template: `plan.md`, `docker-compose.yaml`, `tests/sales.e2e.test.ts`
- Gabarito: `06-rag-neo4j-students-z/` (sem `plan.md`)
- `.env.example`: `OPENROUTER_API_KEY` + LangSmith. Neo4j via compose.

## Comandos

```bash
cp .env.example .env
npm ci
npm run docker:infra:up
npm run seed
npm run test:e2e          # precisa chave + Neo4j
```

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).



Esta pasta é o **gabarito**. Não há `plan.md` aqui — o plano está no template.
