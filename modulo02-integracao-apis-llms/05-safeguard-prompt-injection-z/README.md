# Lab 05 — Safeguard / prompt injection

Demo educativa: o **mesmo** system prompt em modo seguro e `--unsafe`.
Guardrail (modelo safeguard no OpenRouter) vs. só instrução no prompt.
Utilizadores em `data/users.json` (`erickwendel` admin, `ananeri` member).

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.5.

## O que o disco **não** tem

- **Não há pasta `tests/`** neste clone (nem no template nem no `-z`).
- **Não há script `npm test`** no `package.json`.
- O `-z` ainda pode trazer `mcpService.ts`; o foco do checkpoint é o CLI.

## Comandos (precisam `OPENROUTER_API_KEY`)

```bash
cp .env.example .env
npm ci
npm run chat:member:safe
npm run chat:member:unsafe:package
npm run chat:admin
```

Flags: `--user` e `--unsafe`. C02.3: um bloqueio (member+safe) **e** um caso admin.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).


Referências: [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/).


Esta pasta é o **gabarito**.
