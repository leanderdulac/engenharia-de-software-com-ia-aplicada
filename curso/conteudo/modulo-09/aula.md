![Capa do Módulo 09 — Dados e fine-tuning](../../media/imagens/modulo-09-capa.png)

# Módulo 09 — Processamento de dados e fine-tuning (Amplitude Seguros)

Guia: [`curso/modulos/09.md`](../../modulos/09.md). Pasta: [`modulo09-processamento-de-dados-e-fine-tuning-de-modelos/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/). README (custo, env, paridade JS/Python): [`README.md`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/README.md). Carga: ~28 h.

Caso: **Amplitude Seguros** — linhas **Auto** e **Saúde Empresarial**. Há caminho **sem Vertex**: M1–M2 + LoRA MLX/Colab (M4) + harness local (M5.4) + capstone `--local` (M6.2). Documente a escolha.

Companions na **raiz** da pasta (leia cedo): `risco-validade-modelo-companion.md`, `casos-de-mercado-fine-tuning-companion.md`, `disponibilidade-fine-tuning-provedores-companion.md`, `historico-fine-tuning-companion.md`.

Missão: `Atividade N - Módulo N.pdf` **ou** checkpoint. Uma nota só.

---

## Abertura

Fine-tuning, nesta pós, não começa no GPU. Começa em **não treinar**.

A Amplitude tem três casos no JSON da pasta 01. Extração de orçamento de oficina (Auto) tem saída fixa, volume, estabilidade — candidato. Recibo de saúde tem dado sensível (LGPD) e volume ainda baixo. Atendimento ao cliente — negociar contestação em conversa aberta — é o caso que o framework **reprova**: tarefa aberta, política que muda, RAG+HITL já cobrem o rotina. Se o seu entregável “fine-tuna tudo”, você não leu a tool.

Jobs Vertex na gravação da disciplina ficaram entre **R$ 0,86 e R$ 41,40**. Continua sendo billing real. Nomes de modelo no código (`gemini-2.5-flash`, etc.) valiam na gravação; o companion de risco de validade existe porque provedor aposenta versão. Crédito gratuito de cloud **não** é garantia para IA generativa — o README do módulo fala isso sem rodeio.

Ao final: framework nos 3 casos (com um reprovado), JSONL + PII, um treino real (Vertex 200 **ou** LoRA rank 4), um número de harness, ADR próprio. Se o NPV medido matar o fine-tune, isso **é** nota alta — desde que o número venha do harness.

---

## Conceitos (ciclo fechado)

### 9.1 — Quatro perguntas, AHP, NPV, zoo de técnicas

[`modulo-01-decision-framework/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework/)

Rode `decision-framework-tool.js` ou `.py` com [`amplitude-seguros-casos.json`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework/amplitude-seguros-casos.json). Há `limiarVerde`, matriz AHP de Saaty (pesos **não** chutados a dedo) e um **gate binário de governança** antes da conta: dado sensível + DPA. Saúde Empresarial testa esse gate (Art. 5º, II da LGPD no comentário do JSON). Atendimento pinta scores baixos em p1 (tarefa aberta) e p4 (instabilidade regulatória) de propósito.

Também na pasta: `grpo-verifiable-reward-demo`, `fine-tuning-types-cheatsheet.md` (tipos e requisito de dado/hardware), `fine-tuning-zoo-poster.html`, checklist. Papers LoRA e QLoRA estão no syllabus (`2106.09685`, `2305.14314`). Você não precisa treinar QLoRA neste clone; precisa saber **quando** full FT é overkill.

As quatro perguntas, no espírito do JSON (não substituem a tool): a tarefa é **estruturada** o bastante para um schema estável? Prompt+RAG+HITL **já foram** esgotados de verdade? Há **dado** suficiente e diverso? A política de saída é **estável** no horizonte do NPV? Atendimento quebra a primeira e a quarta de propósito, com score alto na segunda e na terceira — volume não salva tarefa aberta. Auto passa com folga e ainda traz bloco `financeiro` (volume 8000/mês, custo por chamada status quo versus fine-tuned, treino 2400, 24 meses, desconto 1%/mês). Saúde trava em p3 (dado) e exige DPA porque procedimento médico é categoria sensível. Rode a tool; não recaia a matriz AHP “no olho”.

### 9.2 — Dataset é produto

[`modulo-02-preparacao-datasets/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-02-preparacao-datasets/)

Imagens sintéticas em [`documentos-brutos/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-02-preparacao-datasets/documentos-brutos/). Tools de extração, limpeza, scoring, PII. `dataset-amplitude-seguros.jsonl` é demo curto. `ocr-vs-llm-extracao-comparativo.md` contrapõe Tesseract/pipeline e Gemini multimodal (`extracao-llm-multimodal-tool`). Dedup: MinHash + LSH (paper Lee et al., `2107.06499`). Balancear Auto versus Saúde. Higienizar PII **antes** de mandar a um endpoint.

JSONL: um JSON por linha, schema estável. Sem schema, o harness do M5 vira teatro. Sem dedup, o modelo decora o mesmo recibo. Sem PII, você vaza segurado no Git — o lab existe para o gate falhar na sua cara, não na do DPO.

Não misture no mesmo arquivo linha de Auto (`placa`) com linha de Saúde (`procedimento`) sem um campo `linha` discriminador. O harness depois parte os sets (`amplitude-auto-only-120.jsonl`, `amplitude-saude-only-80.jsonl`) exatamente para pegar regressão cruzada. Schema frouxo hoje é métrica mentirosa amanhã.

### 9.3 — Fine-tuning via API (Vertex)

[`modulo-03-fine-tuning-via-api/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-03-fine-tuning-via-api/)

`gcp-setup-companion.md` (Passo 0). Dataset `dataset-treinado.jsonl` (200 linhas). Tools de upload, hiperparâmetro, automação, versionamento. `model-card-*.md`. Variáveis: `GCP_PROJECT_ID`, `TUNING_JOB_NAME`, depois `ENDPOINT_MODULO32`. Scripts **param** se a env falta — não usam projeto de terceiro.

Se você **não** vai pagar Vertex, leia o companion, descreva o job com evidência do material (model card, hiperparâmetros) e siga LoRA. O guia aceita Vertex **ou** LoRA/Colab no C09.3. Mentir um `job id` não.

### 9.4 — LoRA / PEFT de verdade

[`modulo-04-lora-e-peft/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft/)

`local-lora-training-tool.js/.py`, configs rank **4 / 8 / 16**, `mlx-data/`, notebook Colab + `colab-lora-training-companion.md`, `guia-execucao-local-modulo-4-companion.md`. Pastas `mlx-adapters*` têm `adapter_config.json`. **Não** têm `adapters.safetensors` — pesos grandes fora do Git (até ~1,9 GB). Você treina. Companions de comparação with/without adapter e entre ranks.

Rank baixo = menos capacidade, menos overfit fácil, menos arquivo. Rank 16 não é “melhor”: é outra curva. Full fine-tuning aparece no material como contraste caro. Apple Silicon via MLX; demais mortais via T4 no Colab.

### 9.5 — Harness: número ou não treinou

[`modulo-05-avaliacao-modelos/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-05-avaliacao-modelos/)

`model-evaluation-harness-tool`, A/B, estresse de formato, `veredito-escala`, NPV **real versus projetado**. Datasets `amplitude-auto-only-120.jsonl` / `amplitude-saude-only-80.jsonl`. `casos-llm-as-judge-companion.md`. Colab de eval para a rota local.

O eval gate do TrialForge (M08) era o portão. Aqui você **passa o modelo no detector de metal**: formato quebra? Auto funciona e Saúde desaba? O NPV do slide sobrevive ao custo real? LLM-as-judge tem os quatro casos no companion — não é metricinha inventada na hora da ata.

### 9.6 — Capstone

[`modulo-06-projeto-final/`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-06-projeto-final/)

`amplitude-seguros-assistente.js` (Vertex; `--local` opcional), `chamar_modelo_local.py`, dataset [`amplitude-seguros-dataset-producao-3000.jsonl`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-06-projeto-final/amplitude-seguros-dataset-producao-3000.jsonl), [`decisoes-de-arquitetura.md`](../../../modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-06-projeto-final/decisoes-de-arquitetura.md), guias de reavaliação e geração sintética, Colab M6.2. `ENDPOINT_MODULO63` só se você publicou o modelo de 3k.

O `decisoes-de-arquitetura.md` de exemplo discute regressão de formato no Round 2 — o ponto é **discordar com evidência**, não copiar as oito decisões. C09.5 pede ADR **seu**.

Rode tools a partir do layout do repo: imports cruzam pastas.

---

## Passo a passo

1. Companions de risco e disponibilidade. Cinco minutos que evitam job morto.
2. Decision tool nos **3** casos. Fotografe o reprovado (Atendimento).
3. Uma imagem de `documentos-brutos/` no gate PII + extração. JSONL com schema. Olhe o comparativo OCR vs multimodal.
4. **Uma** rota de treino: Vertex 200 **ou** LoRA rank 4 (MLX ou Colab). Guarde log / job name / path do adapter. Sem safetensors no Git do curso — no seu workspace local, sim.
5. Harness: uma métrica numérica. Mesmo local.
6. Oito decisões no estilo do ADR de exemplo. Pode matar o fine-tune.

---

## Armadilhas

- **Treinar o caso de Atendimento.** O JSON está calibrado para reprovar. Override sem AHP novo é fanfic.
- **Pular PII porque “é sintético”.** O gate é o exercício.
- **Commits com `adapters.safetensors` no clone da pós.** Os pesos **não** vêm no Git de propósito. Não “complete” o repo.
- **Assumir crédito GCP em Gemini/Vertex.** Leia o README do módulo.
- **Modelo aposentado.** `risco-validade-modelo-companion.md` antes do job pago.
- **NPV só no slide da pasta 01.** O harness confronta projetado versus medido.
- **Dataset 3000 como se fosse rótulo humano perfeito.** Há guia de sintético. Trate qualidade como hipótese a reavaliar (`guia-reavaliacao-pos-escala.md`).
- **Misturar Amplitude com TrialForge no mesmo ADR.** Casos âncora não se misturam no entregável.

---

## Síntese

Você fechou a trilha com a decisão mais cara: **mudar pesos**. O curso obrigou governança, schema, dedup, PII, treino pequeno, harness e ADR. Agente (M04/M08), RAG (M01/M06) e regra (M08 tool) continuam no menu. Fine-tune entra quando a saída é estável, o dado basta, o prompt já foi esgotado e a conta fecha.

A frase de formatura da disciplina: se o harness matar o projeto, você aprendeu. Se o slide salvar o projeto, você não mediu.

Três recusas legítimas que ainda valem nota: (1) Atendimento fora do fine-tune, com AHP colado; (2) Saúde esperando mais recibos, com p3 baixo e DPA ok — você **não** treina no vazio; (3) Auto treinado em rank 4 cujo NPV medido ficou abaixo do projetado, então o ADR recusa promoção. O capstone `--local` e o Colab existem para ninguém ficar de fora por billing. O que não existe é fine-tune imaginário. Companions de mercado e histórico (raiz da pasta) dão repertório; não substituem o JSON dos três casos nem o harness.

---

## Exercício de fixação

Ciclo fechado, Amplitude ou seu domínio no mesmo molde:

1. Print da tool com os 3 casos e o reprovado visível.
2. Amostra JSONL (poucas linhas) + evidência do gate PII numa imagem de `documentos-brutos/`.
3. Log de **um** treino (Vertex ou LoRA/Colab) — sem colar chave.
4. Um número do harness (A/B, formato, ou NPV).
5. ADR de 8 decisões. Se a decisão 8 for “não promover”, justifique com o item 4.

Isso é o projeto do módulo no guia. C09.1 a C09.5 cabem nesse pacote. Leia o companion de validade de modelo e marque no ADR a versão que você de fato usou.
