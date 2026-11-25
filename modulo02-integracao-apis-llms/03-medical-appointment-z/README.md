# Lab 03 — Agendamento médico (LangGraph)

Grafo de **consultas médicas**: intent estruturado → serviço (`appointmentService`) → mensagem.
Nós em `src/graph/nodes/` (`identifyIntentNode`, `schedulerNode`, `cancellerNode`, `messageGeneratorNode`).
Prompts em `src/prompts/v1/`.

O README anterior era cópia de um “Prompt Chaining Article Generator” e **não descrevia este código**.
O `package.json` ainda pode chamar-se `prompt-chaining-article-generator` (nome herdado).

Guia: [`curso/modulos/02.md`](../../curso/modulos/02.md) § 2.3.

## Template vs gabarito

| Pasta | Papel |
| --- | --- |
| `03-medical-appointment-template/` | `identifyIntentNode` devolve o estado quase vazio — já preenchido (gabarito) |
| `03-medical-appointment-z/` | gabarito; abra **depois** |

## Env e comandos

```bash
cp .env.example .env   # OPENROUTER_API_KEY; LangSmith opcional
npm ci
npm run langgraph:serve
npm test               # E2E com API (bloqueado sem chave)
```

Teste no disco: `tests/router.e2e.test.ts`. C02.2 pede o **template** preenchido.

**Node:** vários `package.json` deste módulo declaram `engines.node` `>=24.10.0` ou `v24.14.0`.
A trilha da pós recomenda **Node 22**. Teste no 22; se o runtime recusar (strip-types / EBADENGINE),
documente a versão — não troque o lab. Inspector MCP não entra neste módulo (ver M03).
