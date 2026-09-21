![Capa do Módulo 01 — Fundamentos de IA e LLMs](../../media/imagens/modulo-01-capa.png)

# Módulo 01 — Fundamentos de IA e LLMs para programadores

Guia operacional: [`curso/modulos/01.md`](../../modulos/01.md). Pasta de labs: [`modulo01-fundamentos-de-ia-e-llms-para-programadores/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/). Carga sugerida: ~36 h.

Esta aula é o texto que você lê antes (e durante) os labs. O guia ao lado continua sendo o checklist. Aqui o objetivo é outro: você sair com um modelo mental de engenheiro — o que roda onde, o que custa token, o que precisa de Docker, e por que RAG não é “colar o PDF no prompt”.

---

## Abertura

Você já escreve software. Este módulo não pede que vire cientista de dados. Pede que trate **modelo como componente**: um binário no Node, um worker no browser, uma Prompt API no Chrome, um processo Ollama na máquina, um POST no OpenRouter, um índice de embeddings no Neo4j.

A tentação do mercado é pular direto para o chat. A trilha deste repositório faz o caminho inverso de propósito. Primeiro você treina uma rede **pequena** e vê época, loss e tensor. Depois coloca um recomendador **no navegador**. Depois um detector YOLO atira no pato. Só então o texto entra: temperature, prompt, MCP, e finalmente RAG com retrieval **visível**.

Se você pular o classificador e o Duck Hunt, o Módulo 09 (fine-tuning) e o Módulo 08 (arquitetura) vão parecer magia. Não são. São as mesmas ideias — vetor, amostragem, contexto — em escala de produção.

Ao final desta aula você deve conseguir apontar, com pasta, a diferença entre:

- um modelo **seu**, treinado no `tfjs-node`;
- um modelo **congelado** de visão (YOLO) rodando no cliente;
- um LLM **no dispositivo** (Prompt API);
- um LLM **local** (Ollama) versus **via gateway** (OpenRouter);
- um LLM **com documentos** (RAG no Neo4j).

---

## Conceitos (com o chão deste repositório)

### Rede, tensor e o que a máquina realmente vê

Em [`exemplo-00-template/index.js`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-00-template/index.js) não há “Erick, 30 anos, gosta de azul”. Há um vetor:

`[0.33, 1, 0, 0, 1, 0, 0]` — idade normalizada + one-hot de cor + one-hot de cidade.

O comentário no arquivo ainda mostra as pessoas. O treino usa só números. Isso não é detalhe pedagógico: é o contrato. LLM, YOLO e embedding fazem a mesma conversão — texto ou pixel vira tensor — só que com milhões de parâmetros a mais.

O template 00 para **antes** do `model.fit`. Seu trabalho é completar a rede, treinar e predizer. O gabarito está em [`exemplo-00-z/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-00-z/) (`npm start`). Diff depois, não antes.

No e-commerce, a mesma ideia vira produto. Em [`exemplo-01-ecommerce-recomendations-template/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-01-ecommerce-recomendations-template/) o treino mora num **worker** (`modelTrainingWorker.js`), não na thread da UI. `npm start` sobe o browser-sync na porta **3000** — ignore o 8080 se algum README interno ainda citar essa porta. Os snapshots em [`exemplo-01-ecommerce-recomendations-z/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-01-ecommerce-recomendations-z/) (`parte01-…` até `parte05-…`) quase não mudam a loja: o que evolui é o worker. Compare `parte01` com `parte05` e você vê o curso inteiro em miniatura — o modelo amadurece, a vitrine permanece.

### Inferência no cliente não é LLM

Duck Hunt, em [`exemplo-02-vencendo-qualquer-jogo/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-02-vencendo-qualquer-jogo/), usa um YOLO (`machine-learning/yolov5n_web_model/`) para achar o pato na tela. Comece em `_template/`, depois `DuckHunt-JS-parte01/` (modelo carregado) e `DuckHunt-JS-parte02/` (detecção com threshold). `npm start` sobe em **:8080**.

Aqui a lição de arquitetura: visão no browser tem latência de frame, não de round-trip. Não tem prompt. Não tem token. Se o threshold estiver errado, o jogo erra o tiro — métrica visível, sem dashboard. Guarde isso para o dia em que alguém quiser “um agente” para um problema que é só um classificador.

Aulas 1.1, 1.2, 1.5 e 1.6 **não têm pasta**. São links no [README da raiz](../../../README.md) (Teachable Machine, anatomia de rede, Genetic Cars, transformers). Faça o Teachable Machine se quiser um modelo de imagem no browser sem código. Não trave o módulo nelas.

### LLM: amostragem, não oráculo

Quando o texto entra, o modelo não “sabe”. Ele amostra o próximo token. Dois knobs que este curso obriga você a **sentir**:

- **Temperature** — quão plana é a distribuição. Zero ≈ guloso; um ≈ criativo e instável.
- **Top-K** — quantos tokens candidatos entram no sorteio.

O laboratório é [`exemplo-04-webai02-temperature-and-topK/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-04-webai02-temperature-and-topK/) (`npm start`, sliders). Faça a **mesma** pergunta em temperature 0 e 1 e anote. Isso vira argumento no M04 (orçamento de contexto) e no M07 (você não deixa o LLM inventar P50 de prazo).

Antes dos sliders, [`exemplo-03-webai01/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-03-webai01/) é um `index.html` com Prompt API em streaming. [`exemplo-05-webai03-multimodal/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-05-webai03-multimodal/) acrescenta imagem/áudio e flags do Chrome. Se `LanguageModel` falhar, o caminho documentado é [`troubleshooting/google.md`](../../../troubleshooting/google.md). O checkpoint C01.2 aceita fallback **documentado** — não precisa travar a semana no Chrome Canary.

Prompt engineering (aula 1.8) também não tem pasta de código. O README da raiz, seção 6, trata JSON, TOON e guias de provedor. A regra da casa: **saída estruturada** (JSON ou TOON) quando um programa for consumir a resposta. Texto livre é para humano. Você vai reencontrar isso no Pix (M05), no Requirements Copilot (M07) e no intent médico (M02).

### MCP sem mistério (ainda não é o Módulo 03)

MCP é um contrato: o **host** (Cursor, Copilot, Inspector) fala com um **servidor** que expõe tools, resources e prompts. Neste módulo você **consome** servidores prontos. No M03 você **escreve** o servidor.

Quatro pastas, uma missão cada:

| Pasta | O que você faz de verdade |
| --- | --- |
| [`exemplo-06-playwright-testes/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-06-playwright-testes/) | Cola os prompts + `example.mcp.json` e **gera** o projeto. Não há `tests/` commitados. |
| [`exemplo-07-playwright-navegacao/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-07-playwright-navegacao/) | Segue `prompt.md`: formulário Sessionize **sem** submit. |
| [`exemplo-08-context7/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-08-context7/) | `prompt.md` **ou** rode o `nextjs-better-auth-demo/` já pronto. |
| [`exemplo-09-grafana-mcp/alumnus/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-09-grafana-mcp/alumnus/) | Docker da stack + prompts em `docs/grafana-mcp-prompts.md` para investigar leak. |

Não precisa dos quatro no mesmo dia. O checklist pede **um** MCP completo. O MCP de contribuições citado no README da raiz aponta para um repositório externo — **não está neste clone**. Ignore.

### Local versus nuvem, e depois RAG

[`exemplo-10-ollama/request.sh`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-10-ollama/) e [`exemplo-11-openrouter/request.sh`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-11-openrouter/) mandam o **mesmo** tipo de chamada para dois runtimes. No 11, crie `.env` com `OPENROUTER_API_KEY` — não há `.env.example` neste clone. Anote latência, qualidade e se o dado saiu da máquina. Essa tabela reaparece no TrialForge (M08) como decisão de arquitetura, não como preferência pessoal.

RAG, neste curso, não é “aumentar o prompt”. É **buscar** trechos e só então gerar. O paper está no README da raiz e no [syllabus](../../syllabus.md): Lewis et al., arXiv `2005.11401`. A prática:

1. Template [`exemplo-12-embeddings-neo4j-template/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-12-embeddings-neo4j-template/) — siga `script.txt` (`config.js`, `documentProcessor`, `VectorStoreManager`, `docker compose`, `tensores.pdf`).
2. Gabarito de embeddings [`exemplo-12-embeddings-neo4j/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-12-embeddings-neo4j/).
3. RAG [`exemplo-13-embeddings-neo4j-rag/`](../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-13-embeddings-neo4j-rag/) — `src/ai.ts`, `prompts/`. A pasta `respostas/` é gabarito de saída: leia **depois**.

O retrieval precisa aparecer: ids ou trechos. Sem isso, você não tem RAG — tem um LLM educado. O M02 vai gerar Cypher sobre outro grafo (alunos/cursos). O M06 vai buscar runbook. O M08 vai colocar RAG atrás de um gateway. A peça que você monta agora é a mesma.

`script.txt` do template 12 não é enfeite: lista `config.js`, `util.js`, `documentProcessor`, embeddings visíveis, `VectorStoreManager.addDocuments` / `clearAll`, `docker compose`, `tensores.pdf`. Se o Neo4j subir e o índice ficar vazio, a pergunta do 13 “funciona” com alucinação educada — e o checkpoint C01.4 zera. Browser Sync da loja na 3000 e Duck Hunt na 8080 no mesmo dia confundem porta; anote. Visualizadores do README da raiz (CNN Explainer, Netron) ajudam a ver camada e grafo de rede, mas não substituem o `model.fit` que você tem que completar.

---

## Passo a passo (pastas reais)

Ordem pedagógica da [trilha](../../trilha-aprendizado.md). Trabalhe no template; abra `-z` depois.

1. **Setup.** Node 22, Chrome, Docker Compose v2. Windows: [guia do aluno](../../guia-do-aluno.md) e [`troubleshooting/windows/commons.md`](../../../troubleshooting/windows/commons.md) (`tfjs-node` costuma doer).
2. **Aula 1.3 — classificador.** Complete `exemplo-00-template` até `model.fit` + uma predição. Rode `exemplo-00-z` só para conferir o formato da saída.
3. **Aula 1.3 — loja.** `cd exemplo-01-ecommerce-recomendations-template && npm start` → `http://localhost:3000`. Treine o worker. Depois abra `exemplo-01-ecommerce-recomendations-z/parte01-ecommerce-recomendations-with-tensorflow/` e `parte05-*` e diff em `modelTrainingWorker.js`.
4. **Aula 1.4 — Duck Hunt.** `_template/` → jogue. `DuckHunt-JS-parte01/` → modelo no ar. `parte02/` → threshold. Anote um falso positivo ou um miss.
5. **Aula 1.7 — Web AI.** Abra o `index.html` do exemplo 03. No 04, duas gerações da mesma pergunta (T=0 e T=1). No 05, só se as flags do Chrome cooperarem.
6. **Aula 1.10 — um MCP.** Escolha 06, 07, 08 ou 09. Cole o prompt. Não improvise pasta de testes no 06: o projeto é gerado.
7. **Aula 1.11.** Suba o Ollama, rode `request.sh` no 10. Copie a chave OpenRouter no 11 e repita. Dez linhas de comparação bastam para o projeto do módulo.
8. **Aula 1.12.** `npm ci` e `npm run infra:up` no template 12. Implemente o que `script.txt` lista. Só então olhe o 12 completo e o 13. Entregue: comando do Neo4j, uma pergunta, trechos recuperados, resposta do LLM.

Agentes de código (aula 1.9) são preparação mental para o M04 U1: Ask versus Edit versus Agent, Spec-Kit, worktrees. Sem pasta aqui. Não “implemente um agente” neste módulo.

---

## Armadilhas

- **Abrir o `-z` no primeiro `npm start`.** O gabarito ensina o formato, não o raciocínio. O checkpoint C01.1 pede 00 **ou** 01 rodando — o seu, não o da pasta pronta.
- **Porta do e-commerce.** README interno pode falar 8080; o mapa do repositório e o guia do módulo mandam **:3000**. Duck Hunt é que usa 8080.
- **`tfjs-node` no Windows nativo.** Binário nativo. WSL é o caminho estável; a skill `windowsfy` não milagra binding C++.
- **Prompt API ausente.** Não é falha sua. Documente o Chrome, a flag e o fallback (Ollama/OpenRouter). C01.2 aceita isso.
- **Quatro MCPs no mesmo sábado.** O guia pede um. Grafana (exemplo 09) envolve Docker; Playwright 06 não tem testes no Git.
- **Exemplo 11 sem `.env.example`.** Crie o arquivo. Não commite a chave.
- **`respostas/` do exemplo 13 como “sua” entrega.** O avaliador quer a pergunta que **você** fez e os trechos que **seu** índice devolveu.
- **Achar que RAG do PDF = RAG Cypher do M02.** Um recupera trechos vetoriais; o outro gera consulta de grafo. Mesma família, contrato diferente.

---

## Síntese

Neste módulo a IA deixou de ser um site e virou três lugares de execução: **cliente** (TF.js, YOLO, Prompt API), **processo local** (Ollama, Neo4j no Docker) e **API** (OpenRouter). Você calibru amostragem, escreveu prompt com formato, ligou um servidor MCP como consumidor, e fechou o ciclo embeddings → retrieval → geração.

A frase que vale levar para o M02: o LLM só é componente de sistema quando a saída tem contrato (JSON, tool, Cypher, trecho citado) e quando você sabe **qual runtime** respondeu.

---

## Exercício de fixação

Entregue um único documento curto (Markdown ou PDF) com quatro blocos. Não precisa dos nove exemplos.

1. **Uma rede no disco.** Screenshot ou log de `exemplo-00` ou da loja na :3000, mais duas frases: o que é época e o que é loss **neste** treino.
2. **Uma amostragem.** A mesma pergunta no exemplo 04 com temperature 0 e 1 (ou fallback Ollama, se a Prompt API falhou). Uma linha sobre o que mudou.
3. **Um MCP.** Qual pasta (06–09), o prompt colado, o resultado visível (teste gerado, form preenchido, demo Next, ou hipótese do leak no Grafana).
4. **Pipeline 12 → 13.** Comando para subir o Neo4j, a pergunta, ids/trechos recuperados, a resposta do LLM, e até dez linhas Ollama versus OpenRouter (exemplos 10 e 11) para o mesmo prompt.

Isso é o projeto do módulo no [guia](../../modulos/01.md). Se faltar o 13, o 12 preenchido ainda demonstra embeddings — mas o checkpoint C01.4 pede retrieval visível: complete o RAG.
