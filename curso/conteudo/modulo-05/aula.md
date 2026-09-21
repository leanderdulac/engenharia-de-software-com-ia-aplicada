![Capa do Módulo 05 — IA para UI/UX](../../media/imagens/modulo-05-capa.png)

# Módulo 05 — Ferramentas de IA para UI/UX

Guia: [`curso/modulos/05.md`](../../modulos/05.md). Pasta: [`modulo05-ferramentas-de-IA-para-UI-UX/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/). README do módulo: [`README.md`](../../../modulo05-ferramentas-de-IA-para-UI-UX/README.md) — a árvore com nomes longos (`modulo-01-discovery-refinement/` etc.) **não existe** neste clone. Use `modulo-01/` … `modulo-05/`. Professor no README: Alvaro Camillo Neto. Carga: ~20 h. Live Safer: [`lives/2026-07-28/`](../../../lives/2026-07-28/).

Firebase aparece no README do módulo; o BragBot **não** usa Firebase Hosting. Não bloqueie o lab por isso. Jules e Antigravity estão nos links da raiz e **não** têm pasta aqui.

---

## Abertura

Até agora a IA falava com API, grafo e incidente. Neste módulo ela entra no ciclo de **produto**: briefing ruim, feedback de usuário, tela, spec de change, teste E2E, um backend que transforma texto informal em documento.

O fio é um Pix agendado que nasce ambíguo e vira app Angular; um monorepo Nx de plataforma (CFP) onde a change é contrato; e o **BragBot**, que recebe “fechei o lab do OpsPilot” e devolve um brag estruturado via Genkit.

A competência de saída não é “gerar um layout bonito”. É **curadoria**: prompt versionado, artefato no Git, e uma frase do que a IA **não** fez — você fez.

Pode rodar em paralelo com o M07 (mesmo estilo AI Studio) depois dos prompts do M01. Não depende do OpsPilot.

---

## Conceitos (pastas reais)

### Discovery é estresse de briefing, não brainstorm

[`modulo-01/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-01/) é o único com README pedagógico nesta pasta. O ticket bruto está em [`docs/refinement/briefing-bruto.md`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-01/docs/refinement/briefing-bruto.md): agendar Pix, contato, valor, data, comprovante, limite R$ 5.000, não agendar para o mesmo dia, botão de cancelar. Cabe num parágrafo. Por isso explode em edge case.

Prompts em [`prompts/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-01/prompts/): `system-instructions-refinement.md`, `insights-distiller.md`, `data-sanitizer.md`, `ux-writing-system.md`, `readme-generator.md`. Cole no Google AI Studio como System Instructions. Temperature baixa — o README interno fala em saída determinística.

Dados: `data/raw-feedbacks.json` → sanitizar → `data/sanitized-feedbacks.json` e `data/backlog.json` (referência). Relatórios de aula em [`report/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-01/report/) (singular). O README interno pede `reports/` (plural), `edge-cases.md` e `fluxo-logico.mmd` que **não** estão versionados. Entregue equivalentes em `report/` ou no seu fork. Não invente que o Mermaid já está no Git.

O gesto: a IA lista falhas (agendar para feriado? Pix para si mesmo? fuso?). Você decide o que entra no backlog. Data discovery não é “o modelo leu os comentários”: é JSON in, JSON out, com sanitizer no meio.

Três falhas clássicas desse briefing, para você não esperar a IA descobrir sozinha: (1) “não pode o mesmo dia” não define fuso nem o instante em que “hoje” vira “amanhã”; (2) o limite de R$ 5.000 é diário, mas o texto não diz se agendamentos futuros consomem a cota do dia da **execução** ou do dia do **pedido**; (3) cancelar depois exige estado — comprovante não é a tela de gestão. Se o modelo devolver um fluxo feliz em três telas sem esses estados, o prompt de refinement não estressou o bastante — ou você aceitou a primeira geração.

Nos `report/` da pasta há saídas de aula (`refinamento-pix-aula-1.md`, mermaid, ux-writer). Use como **formato**, não como resposta pronta da sua turma. O sanitizer (`data-sanitizer.md`) existe porque feedback bruto traz xingamento, dado pessoal e ruído. Backlog priorizado sem sanitizar é backlog contaminado.

### Handoff Stitch/Figma → Angular

[`modulo-02/pix-app/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app/). `briefing/` (Stitch, Figma, branding), `stitch/comprovante_stitch.html`, `imagem/extrato-pix.png`, `prompts/` (figma-to-angular, tokens, a11y). A app tem `pix-transfer`, `pix-history`, `pix-receipt`, `error-modal`. README da pasta = Angular CLI.

Aqui a IA não “substitui o Figma”. Ela reduz a distância entre o HTML/Stitch e o componente. Você aplica **um** prompt a **um** componente e mostra o diff. Acessibilidade e tokens não são afterthought: estão nos prompts de propósito. Se a conta Stitch/Figma falhar, ainda dá para trabalhar a partir dos artefatos já na pasta (`stitch/`, `imagem/`).

Olhe o comprovante em `stitch/comprovante_stitch.html` ao lado de `pix-receipt`. Onde o HTML de marketing virou componente Angular? Onde o modal de erro (`error-modal`) cobre o “Pix acima do limite” que o briefing mal mencionou? Esse gap é o exercício de handoff: a IA acelera boilerplate; o estado de erro continua decisão de produto. Angular 21 / Nx no CFP pedem Node na versão da trilha (22). Não misture o app Pix (CLI simples) com o monorepo CFP no mesmo `npm install` na raiz de `modulo05-…`.

### OpenSpec no monorepo: a change é o produto

[`modulo-03/cfp-platform/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform/). Nx: `api/`, `frontend/`, `shared-types/`, `openspec/`, `.agent/workflows/`. Features arquivadas de CFP/dashboard. Playwright em `frontend-e2e`.

Isso é o primo da U1 do M04, em escala de plataforma. Workflows `opsx-*` em `.agent/` conduzem a change. Você não pede “refatora o front”. Você segue o contrato OpenSpec até um arquivo de spec mudar. O link `https://openspec.dev/` está no README da raiz.

[`modulo-04/cfp-plataform_v1/cfp-platform_v1/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-04/cfp-plataform_v1/cfp-platform_v1/) — **typo no nome da pasta**, é assim no disco. Duplica o M3 com foco E2E/MCP: change `openspec/changes/create-event-tests/`, artefatos `.playwright-mcp/`. Expor contexto da app para o agente de teste é a ponte com o M01 (Playwright MCP) e o M03 (servidor). Não precisa dos dois CFP no mesmo entregável; o guia aceita Pix **ou** CFP no C05.2.

### Genkit: LLM no backend sem teatro de infra

[`modulo-05/brag-bot/`](../../../modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot/). `src/flows.ts`, `src/server.ts` com `POST /api/brag`. `.gemini/GEMINI.md`. `npm run genkit:ui` dispara `genkit start`. Sem `.env.example` neste clone — configure a chave Gemini como o código/README do Genkit local pedir (`@genkit-ai/google-genai`).

O fluxo pedagógico: texto informal (“na sprint eu fechei o HITL do OpsPilot e a war room”) → documento de brag estruturado. Você vira o cliente da própria API. C05.3 pede **um** brag. Não precisa de Firebase.

Se o Genkit UI subir e o POST `/api/brag` devolver prosa sem campos (título, impacto, evidência), o flow em `src/flows.ts` não está constrangendo a saída — volte ao prompt do flow, não “peça educado” no body. É o mesmo contrato JSON do M01, agora no backend. A live Safer (2026-07-28) complementa o recorte de produto responsável; não substitui o lab.

---

## Passo a passo

1. Abra o briefing bruto. Sem IA. Anote três buracos. Só então rode `system-instructions-refinement.md` no AI Studio. Compare com a sua lista. Salve o Markdown gerado.
2. Rode o sanitizer / distiller sobre `raw-feedbacks.json`. Diff contra `sanitized-feedbacks.json` e `backlog.json`. Onde você discorda do backlog de referência, escreva. Isso é nota, não erro.
3. No Pix App, escolha um prompt de `pix-app/prompts/` e um componente. Diff no Git. Se não houver Figma, use `stitch/comprovante_stitch.html` e `imagem/extrato-pix.png` como fonte.
4. No CFP, um workflow `opsx-*` até a spec mudar. Ou, no v1, a change `create-event-tests`.
5. BragBot: `POST /api/brag` com uma realização sua da pós. Guarde JSON de entrada e saída.

Projeto: escolha **Pix** ou **CFP** ou **BragBot**. Entregue: problema de UX em uma frase, prompt versionado, print da UI (ou do JSON do brag), e o que a IA não fez.

---

## Armadilhas

- **Seguir a árvore do README do módulo.** `modulo-01-discovery-refinement/` não está no disco. É `modulo-01/`.
- **`reports/` versus `report/`.** Entregue onde o clone realmente escreve (`report/`) ou documente o seu path.
- **Pedir conta Firebase para o BragBot.** Não é pré-requisito do código.
- **Gerar o Angular inteiro de uma vez e não ter diff legível.** O exercício pede um componente, um prompt.
- **OpenSpec como “mais um README”.** A change tem que alterar arquivo de contrato.
- **Temperatura alta no refinement.** O ponto é reduzir variabilidade, não brainstorm criativo.
- **Misturar o Pix com o CFP no mesmo zip “para enriquecer”.** O guia pede um eixo. Profundidade vence volume.

---

## Síntese

Você usou o mesmo músculo de prompt estruturado do M01, agora no ciclo discovery → UI → spec → E2E → backend. A IA acelera. O critério de pronto continua humano: backlog que você topa implementar, componente que passa a11y, change que o Nx entende, brag que você assinaria.

No M07 o Requirements Copilot faz o gesto irmão — transcrição vira Gherkin. A diferença é o domínio: frota RouteWise versus Pix. A disciplina de curadoria é a mesma.

Um teste rápido de honestidade no Pix: o comprovante mostra valor e data, mas o briefing pede cancelamento **depois**. Se o seu app não tem tela (ou estado) para listar agendamentos futuros, a IA gerou o caminho feliz e você comprou. No CFP, se o workflow `opsx-*` só gerou um comentário em issue e nenhum arquivo em `openspec/`, a change não aconteceu. No BragBot, se a saída não tem campo que você usaria num 1:1 de carreira, é lero-lero com endpoint. Três produtos, um critério: artefato que sobrevive sem o chat aberto.

---

## Exercício de fixação

Uma página + artefatos:

1. Três buracos que **você** achou no `briefing-bruto.md` antes da IA, e o que o prompt de refinement acrescentou (ou errou).
2. Um diff: componente Pix **ou** arquivo de spec/OpenSpec no CFP **ou** par request/response do BragBot.
3. Frase de curadoria: “A IA não fez ___ ; eu fiz ___ porque ___.”

Isso cobre C05.1–C05.3 se você escolher bem os anexos. Não precisa dos cinco submódulos.
