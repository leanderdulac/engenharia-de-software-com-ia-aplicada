![Capa do Módulo 07 — Gestão de projetos com IA](../../media/imagens/modulo-07-capa.png)

# Módulo 07 — Ferramentas de IA para gestão de projetos (RouteWise)

Guia: [`curso/modulos/07.md`](../../modulos/07.md). Pasta: [`modulo07-ferramentas-de-ia-para-gestao-de-projetos/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/). README: [`README.md`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/README.md). Professor no README: Dr. José Ahirton Batista Lopes Filho. Carga: ~20 h.

Caso único: **RouteWise**, gestão de frota da Conecta Cargas, **140 veículos**. Dez ferramentas, uma pasta cada. O board evolui: leia `jira-estado-board.md` **quando o arquivo existir** (está em 01–07 e 10; **ausente** em 08 e 09).

Missão de cada unidade: `Atividade - Módulo N.pdf` **ou** o checkpoint de [`avaliacao.md`](../../avaliacao.md) — uma nota só. `Exemplo - Módulo N.pdf` é gabarito. Não entregue os dois como se fossem tarefas distintas.

---

## Abertura

Gestão com IA, neste curso, não é “o Gemini vira o PM”. É um **pipeline de artefatos** com curadoria humana: transcrição → backlog INVEST/Gherkin → RICE/WSJF → cronograma → PERT + Monte Carlo **em script** → risco de fluxo → digest e status para audiências diferentes → compliance como código → NL vira card → OKRs que sobrevivem a um scorecard.

O fluxo padrão do README do módulo vale decorar:

1. Vídeo da pós (fora do Git).
2. `*-prompt.md` no System Instructions do AI Studio (temperatura indicada no arquivo).
3. Dados da pasta como mensagem do usuário (ou os do seu projeto).
4. Comparar com `output-exemplo-*`. A **diferença** é a aula de curadoria.
5. Atividade PDF **ou** checkpoint.

Você já treinou prompt estruturado no M01 e no Pix (M05). Aqui o destinatário muda: o board, o sponsor, o auditor. O risco de alucinação também: um P85 inventado pelo modelo vira compromisso de contrato. Por isso o Monte Carlo é **código**.

---

## Conceitos (dez ferramentas, um board)

### 7.1 Requirements Copilot — da fala ao INVEST

[`modulo-01-planejamento-e-escopo/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo/)

- Prompt: `requirements-copilot-system-prompt.md`
- Entrada: `transcricao-discovery-routewise.md` (reunião longa de discovery)
- Apoio: `routewise-jira-import.csv`, `guia-board-routewise.md`, `Como Importar o Backlog no Jira - Módulo 1.md`
- Referência de saída: `output-demo-m1.2-v1.0.md`

A transcrição é barulhenta de propósito. História duplicada, critério de aceite implícito, “a gente precisa de um mapa”. O Copilot extrai épicos, histórias INVEST, Gherkin. Você mata o que é ruído. Importar no Jira é opcional; o CSV existe para quem quiser o board real.

INVEST, neste lab, é tesouro: história Independente, Negociável, Valiosa, Estimável, Small, Testável. Gherkin (Dado/Quando/Então) amarra o aceite. Se o modelo devolver “como gestor, quero um dashboard bonito para ser feliz”, você não tem INVEST — tem slogan. O `guia-board-routewise.md` e o snapshot `jira-estado-board.md` mostram como o time da Conecta Cargas organizou épicos de telemetria, roteirização e conformidade. Não invente um épico “IA preditiva” que a transcrição não sustentou só porque está na moda da pós.

### 7.2 Backlog Scorer — número com flag

[`modulo-02-priorizacao-de-backlog/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-02-priorizacao-de-backlog/) — `backlog-scorer-prompt.md`, `backlog-routewise-input.md`.

RICE (Reach, Impact, Confidence, Effort) e WSJF (SAFe) estão linkados no README da raiz. O scorer **não** decide o trimestre. Ele calcula e **acende flags** (confiança baixa, esforço subestimado, iniciativa política). Sua entrega forte: **três flags das quais você discorda**, com uma frase cada. Concordar com tudo o output-exemplo é o anti-lab.

### 7.3 Scheduling — capacidade não é vontade

[`modulo-03-cronograma-e-capacidade/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-03-cronograma-e-capacidade/) — `scheduling-prompt.md`, `scheduling-routewise-input.md`. Dependências, WIP, what-if (“e se a API de telemetria atrasar duas sprints?”). O modelo é bom para reescrever o plano. Ruim para inventar FTE que a Conecta Cargas não tem.

### 7.4 Probability Forecast — o LLM não sorteia o P85

[`modulo-04-estimativas-e-previsoes/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-04-estimativas-e-previsoes/)

Aqui a pós desenha uma linha vermelha. O prompt `probability-forecast-prompt.md` ajuda a montar PERT (otimista / mais provável / pessimista). Quem **roda** a simulação são os scripts:

- [`monte-carlo-routewise.js`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-04-estimativas-e-previsoes/monte-carlo-routewise.js)
- [`monte-carlo-routewise.py`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-04-estimativas-e-previsoes/monte-carlo-routewise.py)

P50 / P85 / P95 saem do código. Compare com o chute do modelo. Planning Fallacy está nas leituras opcionais do README da raiz. Se os dois números coincidirem demais, desconfie do prompt “ajuste para ficar bonito”.

Como falar o número: P50 não é “a data do cronograma”. É o percentual de simulações que terminaram até ali. P85 é o compromisso mais honesto para sponsor nervoso. Entregar P50 como se fosse P95 é o mesmo pecado de temperature 1 no exemplo 04 — só que agora tem multa de contrato. Rode o script duas vezes: a nuvem de Monte Carlo deve ser parecida, não idêntica linha a linha; se o LLM devolver sempre o mesmo P85 certinho, ele não simulou.

### 7.5 Risk Monitor — AIOps de projeto

[`modulo-05-riscos-e-aiops/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-05-riscos-e-aiops/) — `risk-monitor-prompt.md`, `risk-monitor-data-exemplo.csv`. Anomalia de **fluxo** (aging, correlação, fila) antes de virar crise de release. Não é o CrashLoop do Nexus. É o board adoecendo. O glossário marca essa diferença de propósito.

### 7.6 e 7.7 — Mesma verdade, várias vozes

[`modulo-06-reunioes-turbinadas/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-06-reunioes-turbinadas/) — `meeting-digest-prompt.md`, `transcricao-sprint-review-s2.md`. Ata, ações, JSON de card.

[`modulo-07-status-reports/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-07-status-reports/) — `status-report-prompt.md`. **Três audiências** a partir do mesmo board (time, liderança, cliente/sponsor). Se os três textos forem idênticos, o prompt falhou ou você não editou. Jargão de Jira no e-mail do C-level é bug de produto.

### 7.8 Compliance como código

[`modulo-08-governanca-e-compliance/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-08-governanca-e-compliance/) — sem `jira-estado-board.md`. `compliance-checklist-prompt.md` gera checklist. O dente é o Danger:

- `danger-config-routewise.py`
- `pr-mock-routewise.json` / `pr-mock-falhas.json`
- `guia-demo-danger.md`

`python danger-config-routewise.py --local` nos **dois** mocks: um PR passa, um falha. Submódulo `.gitmodules` (`routewise-danger-demo`) só se for a demo de CI completa. C07.3 pede evidência de falha e de sucesso. IBM Cost of a Data Breach está no README da raiz como leitura opcional — não precisa citar se não leu.

### 7.9 NL → card

[`modulo-09-automacao-de-ecossistema/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-09-automacao-de-ecossistema/) — também sem board markdown. `setup-guide-m9.md`, `nl-to-workflow-prompt.md`, `ecosystem-bot-template.js`, `make-blueprint-m9.json`. Make.com **ou** o bot Node. Slack é cenário, não pré-requisito de nota se o parser Node demonstrar o card.

### 7.10 OKR Aligner

[`modulo-10-portfolio-e-okrs/`](../../../modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-10-portfolio-e-okrs/) — `okr-aligner-prompt.md`. Parte A: validar OKRs (vanidade versus resultado). Parte B: backlog × objetivo. Parte C: scorecard RouteWise + Fintech + E-commerce. C07.4 pede as três partes (RouteWise ou caso próprio no mesmo molde).

---

## Passo a passo

Não precisa das dez atividades PDF. Precisa do músculo de curadoria em quatro checkpoints.

1. **M1.** Cole o prompt, jogue a transcrição, diff com `output-demo-m1.2-v1.0.md`. Marque histórias que você cortaria.
2. **M2 ou M4.** Scorer com três discordâncias **ou** Monte Carlo rodado no script + P50 comparado ao LLM.
3. **M8.** `--local` nos dois JSON de PR.
4. **M10.** A, B e C preenchidos.

Leia o `jira-estado-board.md` da unidade em que estiver (se existir) para não priorizar um card que o board da semana seguinte já matou.

Quando o board evolui e o prompt ainda fala como se a sprint 1 estivesse vazia, o output-exemplo da pasta **atual** prevalece sobre o da pasta anterior. É o mesmo motivo de não misturar snapshots do OpsPilot: o estado do caso âncora é parte da spec.

Projeto do módulo: **dossiê RouteWise** (ou caso próprio no mesmo pipeline): transcrição → backlog → prioridade → um número de Monte Carlo → OKRs. Uma página: onde a IA alucinou e o que você cortou.

---

## Armadilhas

- **Pedir P85 para o modelo e não rodar o script.** O guia é explícito. C07.2 aceita scorer **ou** Monte Carlo — se escolher estimativa, o número vem do JS/Py.
- **Entregar Atividade PDF e checkpoint juntos** na mesma unidade. Uma nota só.
- **Copiar o `Exemplo - Módulo N.pdf` como se fosse sua curadoria.** O exemplo ensina o formato.
- **Procurar `jira-estado-board.md` em 08 e 09.** Não está lá.
- **Três status reports iguais.** Falhou o exercício 7.7.
- **Make.com obrigatório.** O bot `ecosystem-bot-template.js` cobre o parser.
- **Misturar risco do Nexus (pod) com risco do board.** Vocabulário diferente, pastas diferentes.
- **Jira Cloud como bloqueio.** CSV de import no M1 basta para o backlog existir fora da cabeça.

---

## Síntese

RouteWise ensina a pôr IA em **decisão de projeto** sem entregar o critério. Frameworks clássicos (INVEST, RICE, WSJF, PERT, OKR) continuam no volante. O modelo redige, classifica, traduz audiência. O script simula prazo. O Danger quebra o PR. Você corta o card alucinado.

Isso prepara o M08: se o PM não abre mão do P85, a arquiteta não abre mão do Approval Gate.

Curadoria, na prática, é um comentário no Markdown gerado: “rejeitei a história X porque a transcrição só menciona Y uma vez, como desejo”. Sem esse comentário, o avaliador não distingue o seu olho do temperature 0,7 do Gemini. Os `*-prompt.md` já trazem temperatura recomendada — respeite no Studio e **desrespeite** o output quando o board (`jira-estado-board.md`) contradisser o modelo. O board é o estado do caso. O modelo não estava na daily.

Paridade JS/Python no Monte Carlo e no Danger: escolha uma linguagem e cole o comando que você rodou. Os dois scripts devem contar a mesma história numérica, não o mesmo stdout caractere a caractere.

---

## Exercício de fixação

Dossiê de uma página + anexos mínimos:

1. Duas histórias extraídas da transcrição e uma que você recusou (M1).
2. Uma tabela RICE **ou** uma linha `P50=…` saída do script (não do chat).
3. Print ou log: PR mock que falha e PR que passa no Danger.
4. Um OKR validado e um OKR de vaidade que o Aligner (ou você) derrubou.
5. Parágrafo de alucinação: “O modelo inventou ___; eu cortei porque ___.”

Caso próprio é bem-vindo se o pipeline for o mesmo. Não misture com TrialForge neste entregável.
