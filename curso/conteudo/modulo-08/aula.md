![Capa do Módulo 08 — Arquitetura de sistemas com IA](../../media/imagens/modulo-08-capa.png)

# Módulo 08 — Arquitetura de sistemas com IA (TrialForge)

Guia: [`curso/modulos/08.md`](../../modulos/08.md). Pasta: [`modulo08-arquitetura-de-sistemas-com-ia/`](../../../modulo08-arquitetura-de-sistemas-com-ia/). README: [`README.md`](../../../modulo08-arquitetura-de-sistemas-com-ia/README.md). Carga: ~20 h.

Caso de **referência**: **TrialForge** / Vitalis Pharma — geração de documentos clínicos regulatórios (ICF, Protocolo, CSR). Os canvases devem ser preenchidos com **caso próprio**. Copiar o PDF já preenchido da Vitalis não é o C08.1.

Paridade JS/Python nos protótipos. Padrão do módulo: Ollama local (`gemma4:e2b`, ~7 GB) — baixe **antes** da semana. Alternativas pagas: `provedores-pagos.js` / `provedores_pagos.py`. M4.5/M5.4 pedem também `nomic-embed-text` e `gemma4` maior. A tabela local versus pago está no README do módulo: custo, dado, rate limit, qualidade, disco. Cite-a na entrega.

Missão: `Atividade N - Módulo N.pdf` **ou** checkpoint — uma nota só.

---

## Abertura

Os módulos 01–07 construíram peças. Este junta as peças num **diagrama de sistema**: Gateway → Orquestrador → Modelo+RAG → **Approval Gate**, com banda de observabilidade.

A pergunta que paga o salário da arquiteta: **agente ou regra?** Não se responde no feeling. Responde-se com `decision-framework-tool` (JS ou Python) e o checklist. Um classificador de status de estudo clínico pode ser regra. Redigir o ICF com citação de protocolo pede modelo + RAG + humano que assina.

TrialForge é o exemplo rico (dado sensível, auditoria, falha cara). Seu sistema — um checkout, um RH, um Pix — é o que o canvas quer. RAND *Why AI Projects Fail* está no README da raiz como opcional: a falha típica é começar pelo modelo e nunca desenhar o gate.

---

## Conceitos (cinco pastas)

### 8.1 — Diagrama e a decisão agente versus regra

[`modulo-01-fundamentos-ai-first/`](../../../modulo08-arquitetura-de-sistemas-com-ia/modulo-01-fundamentos-ai-first/)

Artefatos: `reference-architecture-canvas.md`, `ai-first-architecture-canvas.md`, `decision-framework-checklist.md`, `decision-framework-tool.js` / `decision_framework_tool.py`. PDFs de apoio: cheat-sheet de clouds, `AI-Architecture-Decision-Canvas.pdf` e o preenchido TrialForge (referência, não cola).

O diagrama de referência não é poster. Cada caixa tem dono:

- **Gateway** — o que o M02 implementou no Fastify e o M04 apontou para OpenRouter: contrato estável, modelo trocável.
- **Orquestrador** — grafo, não “o chat”.
- **Modelo + RAG** — geração com retrieval visível (M01 exemplo 13; aqui, padrão avançado na pasta 04).
- **Approval Gate** — irmão do 202 do OpsPilot e da senha do Nexus. Quem aprova o quê, em qual documento.
- **Observabilidade** — traces e audit trail, não só um `console.log`.

Rode a tool de decisão em pelo menos dois fluxos do **seu** caso: um que deve permanecer regra, um que justifica agente. Anote os eixos que a tool pedir (não invente um framework paralelo).

Exemplo no espírito TrialForge, para calibrar o olhar — **não copie como se fosse o seu canvas**: validar se o estudo está “em recrutamento” a partir de um enum no banco é regra. Redigir o ICF citando cláusula do protocolo, com trecho recuperado e médico responsável, é agente + RAG + gate. No seu Pix, “recusar agendamento acima de R$ 5.000” é regra (o briefing do M05 já deu o número). “Explicar em linguagem de cliente por que o agendamento caiu, com base no comprovante e no regulamento” pode ser geração. A tool existe para você não promover o segundo caso sem custo de avaliação e de aprovação.

`reference-architecture-canvas.md` pede que você desenhe as setas. Se o seu desenho for “usuário → ChatGPT → PDF”, você não fez o módulo: faltam gateway, orquestrador e a banda de log. O cheat-sheet de clouds no PDF da pasta compara provedores; o modelo, como o README insiste, é a peça que se troca.

### 8.2 — Single-agent: anatomia e ReAct de verdade

[`modulo-02-single-agent/`](../../../modulo08-arquitetura-de-sistemas-com-ia/modulo-02-single-agent/)

Canvases: anatomia, ReAct, reflexão, tool schema, blueprint. Protótipos `react-agent-prototype.js` / `react_agent_prototype.py` e `agent-components-demo.js` / `agent_components_demo.py`.

Você já rodou ReAct no OpsPilot e no Nexus. Aqui o exercício é **nomear as peças** (memória, tools, loop, teto) e colar um trace de **um** loop Thought → Action → Observation. MCP volta como contrato de ferramenta, não como lab novo. Se o Ollama não estiver no ar, o protótipo não “ensina arquitetura no papel”: ele falha. Suba o daemon. Ou use o arquivo de provedores pagos, com chave — e cite o trade-off.

### 8.3 — Seis padrões e falha distribuída

[`modulo-03-multi-agent/`](../../../modulo08-arquitetura-de-sistemas-com-ia/modulo-03-multi-agent/)

`orchestration-pattern-selector.md` e `-v2.md`: Sequential, Parallel, Supervisor, Hierarchical, Group Chat, Handoff. O OpsPilot U9 é um ponto nesta lista (supervisor + blackboard + handoff), não a lista inteira. `trialforge-message-queue-prototype.js` / `.py` mostra fila. `distributed-failure-canvas.md` pede CAP e Saga: o que acontece se o agente de CSR confirmar e o de Protocolo falhar no meio.

C08.3: marque **um** padrão e o modo de falha. “Vamos de multiagente porque é o futuro” zera o item.

Handoff não é “os agentes se falam no Slack”. É passagem de estado com contrato (o que o próximo papel precisa, o que não deve reprocessar). Sequential é mais fácil de auditar e mais lento. Parallel explode quando duas escritas no CSR competem. Hierarchical (Nexus lab 12, Manager) concentra decisão e cria gargalo. Escolha com o canvas de falha aberto, não com o slide de moda.

### 8.4 — Padrões só de IA: RAG, rota, cache, HITL

[`modulo-04-padroes-ai-especificos/`](../../../modulo08-arquitetura-de-sistemas-com-ia/modulo-04-padroes-ai-especificos/)

RAG selector, routing, cache/streaming, HITL, `gateway-blueprint-canvas.md`. Protótipo `trialforge-gateway-prototype.js` / `trialforge_gateway_prototype.py`. Referência `audit-trail.jsonl`.

O canvas pede **medição**. Não copie limiar de cache ou de confiança do demo. Paper RAG (Lewis et al., arXiv `2005.11401`) já é velho conhecido do M01: aqui ele ganha ranking, reescrita de query, talvez híbrido — o seletor da pasta diz o que o material cobre. Approval Gate formal: não é flag `awaitHumanApproval` só no JSON; é papel, SLA, evidência no jsonl.

### 8.5 — Enterprise: tiering, eval gate, guardrail

[`modulo-05-arquitetura-enterprise/`](../../../modulo08-arquitetura-de-sistemas-com-ia/modulo-05-arquitetura-enterprise/)

Canvases de stack, sinais de obs, deploy, cascade. Protótipos: `trialforge-model-tiering-prototype` (JS/Py), `model-eval-gate-prototype`, `manipulation-guardrail-prototype`. `audit-trail-tiering.jsonl`.

**Model tiering**: começa barato/local, sobe para fronteira se a confiança ou o tipo de documento exigir. É o gateway do M02 com política. **Eval gate**: modelo novo não vai para o ICF de paciente sem harness — o M09 vai aprofundar o harness; aqui o protótipo mostra o **portão**. Guardrail de manipulação: o usuário (ou um agente vizinho) tenta desviar o CSR; o sistema recusa e registra.

---

## Passo a passo

1. Baixe `gemma4:e2b` cedo. Leia a tabela local vs pago do README.
2. Preencha o canvas M1 com **seu** sistema. Rode a decision tool. Guarde um fluxo “fica regra” e um “vai agente”.
3. `npm install` na pasta 02 (ou Python). Um loop ReAct no terminal. Cole o trace.
4. No seletor M3, um padrão + uma falha (timeout, partição, compensação Saga).
5. Rode gateway **ou** tiering. Diff o jsonl gerado contra `audit-trail.jsonl` ou `audit-trail-tiering.jsonl`. Não precisa os dois protótipos para o C08.4.

Projeto: **3–5 ADRs curtos** + um protótipo M4 ou M5. Defina Approval Gate (quem aprova o quê) e eval gate (o que impede promover modelo). TrialForge só como referência.

---

## Armadilhas

- **Canvas colado do PDF TrialForge.** C08.1 é caso próprio.
- **Limiares do demo no canvas de medição.** O guia grifa isso.
- **Ollama na hora da aula.** São gigabytes. Falha previsível.
- **Chamar multiagente sem modo de falha.** CAP/Saga não são enfeite do canvas.
- **Achar que HITL do OpsPilot encerra o M4 deste módulo.** Lá é HTTP 202 de incidente. Aqui é gate regulatório de documento. Mesmo princípio, contrato diferente.
- **Atividade PDF e checkpoint na mesma unidade.** Uma nota.
- **Inventar URL de framework de decisão.** Use a tool da pasta.
- **Ignorar o trade-off local vs pago** na entrega. O README pede a citação.

---

## Síntese

Arquitetura AI-first neste repositório é um desenho com **portas**: gateway, retrieval, aprovação, promoção de modelo. Agente é uma opção cara — em latência, em falha parcial, em auditoria. Regra continua sendo engenharia de software. O TrialForge só deixa o custo da escolha visível (documento clínico errado não se “hotfixa” com um revert de CSS).

O M09 pergunta a porta seguinte: e se a peça certa não for o agente, for um **peso treinado**? AHP e NPV decidem. O eval gate que você nomeou aqui reaparece como harness.

Escreva os ADRs no tempo presente, com alternativa rejeitada. “Escolhemos Supervisor porque o time já opera plantão; rejeitamos Group Chat porque o CSR não pode divergir em público sem trilha.” Isso é arquitetura. “Usamos IA porque inovação” não é. O protótipo de fila (pasta 03) e o jsonl (pastas 04–05) existem para o ADR não ser só opinião: você cola um `request_id` e diz o que o gate fez. Se o Ollama alucinar cláusula de protocolo, o canvas de HITL ganha uma linha — não “vamos um modelo maior” como único plano.

---

## Exercício de fixação

Pacote mínimo:

1. Canvas M1 do seu sistema (não a Vitalis) + output da decision tool em dois fluxos.
2. Trace de um loop ReAct (Ollama ou pago, com a tabela de trade-off citada).
3. Padrão multiagente escolhido + uma frase de falha distribuída.
4. Um jsonl seu (gateway ou tiering) e o que diferiu da referência.
5. ADR de meia página: Approval Gate e eval gate.

Se o seu caso “não tem o que aprovar”, escolha outro fluxo — ou justifique regra pura com a tool. Justificativa vazia não fecha o C08.1.
