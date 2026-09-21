# Avaliação

Critérios para turma de pós-graduação usando **este** repositório. Adapte pesos ao calendário; não avalie o que o lab não pede e não invente PDFs que não estão no clone.

## Aprovação

- Média ponderada **≥ 7,0**.
- Checklist de conclusão marcado em **pelo menos 7 dos 9 módulos**, incluindo **obrigatoriamente o M04** e **pelo menos um** entre M06, M08 e M09.
- Cada checkpoint abaixo precisa de artefato entregue (repo pessoal, gist, ou pasta no LMS) — não basta “eu rodei”.

Sugestão de pesos (espelha [syllabus.md](./syllabus.md)):

| Componente | Peso |
| --- | --- |
| Checkpoints de lab (M01–M03, trechos do M06) | 30% |
| Projetos âncora de módulo | 50% |
| Curadoria (prompts, canvases, decisões HITL, comparações template vs gabarito) | 10% |
| Integração opcional (cruzar dois casos) | 10% |

Se a turma não fizer integração, redistribua os 10% nos projetos âncora.

---

## Rubrica genérica (0–10)

Use esta grade em **qualquer** entregável de código ou artefato de prompt. Depois aplique os critérios específicos do módulo.

| Nota | Código / lab | Decisão / curadoria | Rastreio |
| --- | --- | --- | --- |
| 9–10 | Roda do README/guia; testes ou demo reproduzível; trata erro de API/chave | Explica *por que* a escolha (modelo, temperatura, HITL, fine-tune ou não) | Commit/histórico ou canvas preenchido com caso próprio |
| 7–8 | Roda o caminho feliz; gaps menores documentados | Curadoria visível (diff vs `output-exemplo` ou vs `-z`) | README de 1 página do que rodou |
| 5–6 | Copia gabarito com pouca alteração; ambiente pela metade | Afirmações sem evidência do lab | Só prints |
| 0–4 | Não executa; pasta errada; inventa API | Entrega genérica de “curso de SE” sem o caso âncora | Nada |

**Cola do gabarito (`*-z`) sem tentativa no template = teto 6,0** naquele lab, salvo o lab não ter template (M02 `01`, `02`, `07`; M03 `02`, `08`, `09`).

---

## Checkpoints por módulo

Entrega mínima para “módulo concluído”. Detalhe do *como* está no guia em [`modulos/`](./modulos/).

### M01 — Fundamentos

| ID | Evidência |
| --- | --- |
| C01.1 | `exemplo-00` ou `exemplo-01` rodando (print ou URL local + `package.json` usado) |
| C01.2 | Um lab Web AI (03, 04 ou 05) **ou** justificativa se o Chrome da máquina não tem Prompt API ([`troubleshooting/google.md`](../troubleshooting/google.md)) |
| C01.3 | Um fluxo MCP (06, 07, 08 ou 09) com o prompt usado colado |
| C01.4 | RAG do `exemplo-13` (ou implementação a partir do template 12): pergunta, chunks recuperados, resposta |

### M02 — APIs

| ID | Evidência |
| --- | --- |
| C02.1 | Router **ou** LangGraph intro com request/response |
| C02.2 | Medical appointment **no template** (não só o `-z`) com pelo menos um E2E passando |
| C02.3 | Safeguard: um ataque `unsafe` bloqueado e um caso admin que passa |
| C02.4 | Cypher lab (`plan.md`) **ou** doc-analysis com PDF próprio (o repo não traz PDF em `07-doc-analysis/docs/`) |

### M03 — MCP

| ID | Evidência |
| --- | --- |
| C03.1 | CipherSuite MCP (`05`) no Inspector **ou** customers MCP falando com a API (`06`) |
| C03.2 | `SERVICE_TOKEN` no lab 07 (chamada recusada sem token, aceita com token) |
| C03.3 | Um entre: publicação Verdaccio (08), Trends+SerpAPI (02), ou LangChain MultiServer (09) |

### M04 — OpsPilot / Notas API

| ID | Evidência |
| --- | --- |
| C04.1 | Notas API: spec + implementação de uma feature via fluxo SDD (U1) |
| C04.2 | Arena/bench (U2) com pelo menos duas estratégias |
| C04.3 | `/chat` + uma tool real (U3) |
| C04.4 | Conversa longa com sumarização visível no trace (U5) **ou** HITL 202 (U7) |
| C04.5 | War room (U8) **ou** rota `team` (U9) |

Projeto âncora do módulo = **C04.3 + (C04.4 ou C04.5)** sobre o snapshot correspondente.

### M05 — UI/UX

| ID | Evidência |
| --- | --- |
| C05.1 | Backlog/relatório a partir de `modulo-01/` (prompt + JSON ou Markdown gerado) |
| C05.2 | Tela Pix **ou** fluxo CFP (M2–M4) com print e o prompt de handoff usado |
| C05.3 | BragBot: um “brag document” gerado via Genkit |

### M06 — Nexus

| ID | Evidência |
| --- | --- |
| C06.1 | Labs 1–2 (S3/IaC) |
| C06.2 | Lab 4 (ReAct) **ou** lab 6 (ChatOps com senha) |
| C06.3 | Um de {7 Trivy, 9 FinOps, 10 RAG} |
| C06.4 | Lab 11 HITL **e** lab 12 relatório executivo |

Projeto âncora = **C06.4**.

### M07 — RouteWise

| ID | Evidência |
| --- | --- |
| C07.1 | M1 Requirements (backlog a partir da transcrição) |
| C07.2 | M2 scorer **ou** M4 Monte Carlo (script, não só o LLM) |
| C07.3 | M8 Danger local com um mock que falha e um que passa |
| C07.4 | M10 OKR Aligner (partes A–C ou caso próprio equivalente) |

Projeto âncora = pipeline **C07.1 → C07.4** no mesmo caso (RouteWise ou o projeto do aluno).

### M08 — TrialForge

| ID | Evidência |
| --- | --- |
| C08.1 | Canvas M1 preenchido com **caso próprio** (TrialForge só como referência) |
| C08.2 | Protótipo ReAct (M2) rodando contra Ollama **ou** `provedores-pagos` |
| C08.3 | Seletor de orquestração (M3) justificado |
| C08.4 | Gateway ou tiering (M4/M5) com comparação ao `audit-trail*.jsonl` |

Projeto âncora = **C08.1 + C08.4**.

### M09 — Amplitude Seguros

| ID | Evidência |
| --- | --- |
| C09.1 | Decision framework nos 3 casos JSON (quem reprova, quem escala) |
| C09.2 | Dataset JSONL limpo (M2) — pode ser o demo + PII gate |
| C09.3 | Um treino real: Vertex **ou** LoRA MLX/Colab (pesos não vêm no Git) |
| C09.4 | Harness de avaliação (M5) com números |
| C09.5 | Capstone: `decisoes-de-arquitetura.md` **próprio** (pode partir do exemplo da pasta M6) |

Projeto âncora = **C09.1 + C09.3 + C09.4**. Sem GCP, C09.3 = Colab/MLX documentado.

---

## Projetos finais por módulo (entrega “de vitrine”)

Não são produtos novos: são **sínteses** do que o repo já constrói.

| Módulo | Entrega de vitrine | Critério de 10 |
| --- | --- | --- |
| 01 | Mini-RAG (ex. 13) + 1 página: local vs OpenRouter | Retrieval visível + falha conhecida documentada |
| 02 | API LangGraph (médico **ou** Cypher) com testes | Template implementado, não só `-z` |
| 03 | MCP + API legado autenticada | Token obrigatório; Inspector ou cliente LangChain |
| 04 | OpsPilot no snapshot U8 ou U9 | HITL ou team mode demonstrado |
| 05 | Um PR/artefato CFP ou BragBot | Prompt versionado + UI |
| 06 | Relatório do lab 12 | Três domínios no mesmo incidente |
| 07 | Dossiê RouteWise (backlog → OKRs) | Curadoria vs `output-exemplo-*` explícita |
| 08 | ADRs + protótipo enterprise | Caso próprio no canvas |
| 09 | Modelo avaliado + ADR | NPV/harness com número medido, não chute |

Integração opcional (os 10%): por exemplo, usar o Requirements Copilot (M07) no briefing Pix (M05), ou o Approval Gate (M08) no OpsPilot (M04). Um parágrafo de arquitetura + demo basta.

---

## O que não avaliar

- Presença nas lives (`lives/`) — salvo combinado no início da turma.
- PDFs `Atividade - Módulo N.pdf` dos M07–M09: **não estão neste clone**; use os checkpoints acima.
- Planos HTML `unidade-N-plano-de-aula.html` do M04: **ausentes** neste clone; use `UNIDADE.md`.
- Pasta `modulo04-agentes-autonomos/` (legado): **não existe** aqui.
- Qualidade gráfica de slides Nexus vs. execução dos labs.

## Feedback rápido (instrutor)

1. O artefato aponta para uma **pasta que existe**?
2. Rodou no **template** quando havia template?
3. Há **diff consciente** em relação ao gabarito/exemplo?
4. A decisão (modelo, HITL, fine-tune) está **justificada com o caso âncora**?
