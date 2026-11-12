# Trilha Avançada: Customização de LLMs

Trilha **opcional**, fora das 240 h de M01–M09. Não altera a grade, os checkpoints C01–C09, o progresso do LMS nem o app em `curso/ead`.

Você já treinou LoRA na Amplitude (M09) e já mexeu em temperature (M01). Esta trilha abre a caixa: o bloco Transformer, o treino token a token, preferências, RL com recompensa verificável, destilação, MoE e serving. Hardware: CPU, Colab gratuito (T4) ou Mac Apple Silicon — modelos de 0,1B a ~1,7B. O curso **não** fornece GPU.

**Pré-requisito da trilha:** M09 concluído (C09.3 e C09.4). Sem isso, os labs posteriores que reusam o harness Amplitude não fazem sentido.

**Licença:** obra nova. A licença desta pasta ainda **não** foi escolhida pelo titular — leia [`LICENSE-PENDENTE.md`](./LICENSE-PENDENTE.md) e [`NOTICE.md`](./NOTICE.md). O tronco continua CC BY-NC-ND 4.0; esta trilha cita M01–M09 sem editá-los.

## Por que existe

No tronco, embeddings de *sentença* e RAG aparecem no M01; LoRA em `q_proj`/`v_proj` aparece no M09; o bloco em si (Q, K, V, máscara causal, RoPE, RMSNorm) **não é aula**. Uma comparação interna de tópicos de customização de LLMs mediu essa lacuna em 0% no bloco Transformer. A trilha fecha isso com texto original e lab executável — sem copiar ementa externa.

O que o tronco já cobre bem (dados, SFT, LoRA/QLoRA, harness, governança, decisão de *não* treinar) **não é reescrito aqui**. Cada módulo aponta para a pasta de M01–M09 correspondente.

## Relação com M01–M09

| Você viu no tronco | Esta trilha acrescenta |
| --- | --- |
| M01: temperature/top-K como sliders; embedding de sentença no Neo4j; “o LLM amostra o próximo token” | A1: tokenização e custo PT/EN; logits→softmax; o laço token a token. A2: o bloco que *produz* esses logits. |
| M04: ReAct / plan-and-execute como **agente** | A7: raciocínio como **dado e treino** (CoT, self-consistency, verificador). |
| M08: tiering, eval gate, “MoE ≠ multiagente” numa nota | A11: MoE de verdade (router, experts, quantização, KV cache, serving). |
| M09: decision framework, JSONL, LoRA/QLoRA, harness, GRPO *sem* atualizar pesos | A3–A6, A8–A10, A12: treino por dentro, máscara do assistant, LoRA de produção, DPO/família, GRPO que treina, destilação, capstone da trilha. |

Rota mínima (~45 h, quando os módulos existirem): A0 → A1 → A2 → A5 → A6 → A8 → A11 → A12 (versão curta). Quem só quer a maior lacuna faz **A2 agora**. A1, A11, A8, A9 e A10 já podem ser cursados depois do A2 (A1 também a partir do M01), com as pontes honestas dos READMEs (sem A0/A3/A5/A6/A7).

## Índice dos 13 módulos

Checkpoints da trilha usam o prefixo **CA** para não colidir com C01–C09. Horas = estudo + lab do aluno, não horas de vídeo.

| # | Módulo | Horas | Pré-req. | Status | Fecha (interno) |
| --- | --- | ---: | --- | --- | --- |
| [A0](./modulo-a0/README.md) | Bancada: ambiente, medição e orçamento de GPU | 2 | M09 (C09.3, C09.4) | esqueleto | versões, memória, `bancada.json` |
| [A1](./modulo-a1/README.md) | Por dentro do LLM: tokens, logits e amostragem | 4 | A0 (ver nota) | **publicado** | tokenização, softmax, top-p |
| [A2](./modulo-a2/README.md) | O bloco Transformer, peça por peça | 6 | A1 (ver nota) | **publicado** | atenção, QKV, máscaras, bloco, decoder-only |
| [A3](./modulo-a3/README.md) | Treino por dentro | 6 | A2 | esqueleto | shift, CE, LR, accumulation, precisão |
| [A4](./modulo-a4/README.md) | Dados para SFT no nível do token | 4 | A1 + M09 M2 | esqueleto | chat template, máscara, EOS |
| [A5](./modulo-a5/README.md) | SFT sério | 6 | A3, A4 | esqueleto | assistant-only, esquecimento, tracking |
| [A6](./modulo-a6/README.md) | LoRA na prática de produção | 5 | A5 | esqueleto | alvos, merge, multi-adapter, GGUF |
| [A7](./modulo-a7/README.md) | Raciocínio treinável | 5 | A1, M04 U2 | esqueleto | CoT, self-consistency, verificadores |
| [A8](./modulo-a8/README.md) | Alinhamento por preferências | 7 | A5, A6 (ver nota) | **publicado** | DPO e família |
| [A9](./modulo-a9/README.md) | RL com recompensa verificável | 8 | A7, A8 (ver nota) | **publicado** | REINFORCE → GRPO |
| [A10](./modulo-a10/README.md) | Destilação | 6 | A5, A7 (ver nota) | **publicado** | professor/aluno, logits, licença |
| [A11](./modulo-a11/README.md) | MoE, quantização e serving | 9 | A2, A6 (ver nota) | **publicado** | experts, PTQ/QAT, KV cache |
| [A12](./modulo-a12/README.md) | Projeto final da trilha | 10 | A5 + dois de A8–A11 | esqueleto | capstone sobre o ADR do M09 |

**Total previsto:** 78 h. Não entram nas 240 h obrigatórias.

### Nota sobre A2 ter saído antes de A1

A ordem de *construção* (A2 → A11 → A8 → A9 → A10 → A1) entregou primeiro a lacuna maior. A1 agora existe: BPE, custo PT/EN, softmax, top-p, laço vs `generate`. Quem já cursou A2 pelo M01 não precisa refazer o bloco; o A1 preenche o sampler que o A2 apontava. A0 continua esqueleto — o JSON do A1 declara ambiente sem `bancada.json`.

A11 oficialmente pede A6; A6 ainda é esqueleto. O módulo declara isso: MoE avulso, PTQ no SmolLM2 do A2, LoRA-MoE (CA11.3) não executa, T4/vLLM não calibrados.

A8 oficialmente pede A5/A6; ambos ainda são esqueleto. O módulo declara isso: DPO no SmolLM2 **base** + LoRA, pares originais no padrão do M09 (sem copiar o JSONL), T4/harness/IC não calibrados.

A9 oficialmente pede A7 e A8; A7 ainda é esqueleto. O módulo declara isso: GRPO no SmolLM2 **base** + LoRA (não o SFT da trilha), recompensa verificável de soma curta, demo GRPO do M09 citado e **não** copiado (aquele script não atualiza pesos). T4 / G grande / IC = `nao_calibrado`.

A10 oficialmente pede A5 e A7; ambos esqueleto. O módulo declara isso: aluno = SmolLM2-135M **base** + LoRA; professor = SmolLM2-360M (Apache-2.0, mesmo tokenizer). T4 / custo/1k = `nao_calibrado`. A queda dos logits (0,383) foi reinvestigada: máscara/shift/T² certos; perda mista α=0,5 chega a 0,567 e ainda não vence a CE.

A1 oficialmente pede A0; A0 é esqueleto. O módulo declara isso: ponte M01 (`exemplo-04`) + A2 já publicado. Qwen2.5-0.5B entra só como tokenizer. T4 / Prompt API / custo/1k = `nao_calibrado`.

## Como rodar o que já existe (A2, A11, A8, A9, A10 e A1)

```bash
cd curso/trilha-avancada
pip install -r requirements.txt          # CPU; no Colab, veja o README do módulo
python modulo-a2/lab/lab_a2.py           # A2.1 + A2.2 → modulo-a2/saidas/ca2.json
python modulo-a11/lab/lab_a11.py         # A11.1–A11.6 → modulo-a11/saidas/ca11.json
python modulo-a8/lab/lab_a8.py           # A8.1–A8.5 → modulo-a8/saidas/ca8.json
python modulo-a9/lab/lab_a9.py           # A9.1–A9.5 → modulo-a9/saidas/ca9.json
python modulo-a10/lab/lab_a10.py         # A10.1–A10.6 → modulo-a10/saidas/ca10.json
python modulo-a1/lab/lab_a1.py           # A1.1–A1.2 → modulo-a1/saidas/ca1.json
python -m pytest -q                      # A2 + A11 + A8 + A9 + A10 + A1; inclui modelos pequenos (marca `modelo`)
python -m pytest -q -m "not modelo"      # só CPU, sem baixar pesos de 135M / configs HF
```

Detalhes, Colab e checkpoints: [`modulo-a2/README.md`](./modulo-a2/README.md), [`modulo-a11/README.md`](./modulo-a11/README.md), [`modulo-a8/README.md`](./modulo-a8/README.md), [`modulo-a9/README.md`](./modulo-a9/README.md), [`modulo-a10/README.md`](./modulo-a10/README.md), [`modulo-a1/README.md`](./modulo-a1/README.md). A11.2 tenta o Granite 1B-A400M; se não couber, o JSON traz `nao_coube` e a config ainda vale. A8.5, A9.5 e A10.6 (T4 / harness / IC / G grande / custo/1k) ficam `nao_calibrado` nesta CPU.

## Tutor socrático (opcional)

Não vale nota. Não substitui CA*. Copie [`tutor/tutor-socratico-ptbr.md`](./tutor/tutor-socratico-ptbr.md) **e** o mapa do módulo (A2: [`modulo-a2/tutor/mapa-a2.md`](./modulo-a2/tutor/mapa-a2.md); A11: [`modulo-a11/tutor/mapa-a11.md`](./modulo-a11/tutor/mapa-a11.md); A8: [`modulo-a8/tutor/mapa-a8.md`](./modulo-a8/tutor/mapa-a8.md); A9: [`modulo-a9/tutor/mapa-a9.md`](./modulo-a9/tutor/mapa-a9.md); A10: [`modulo-a10/tutor/mapa-a10.md`](./modulo-a10/tutor/mapa-a10.md); A1: [`modulo-a1/tutor/mapa-a1.md`](./modulo-a1/tutor/mapa-a1.md)) no assistente. Origem MIT: Jane Street; ver NOTICE.

## Leitura extra (Apache-2.0, isolada)

O fork `leanderdulac/curso-de-engenharia-de-IA` (upstream `lucianoon/llm-course`) tem módulos 01–12 sobre temas parecidos. Neste clone só estão 06, 13 e 19, em [`referencia/llm-course/`](../../referencia/llm-course/). Crédito: [`curso/ATRIBUICOES-llm-course.md`](../ATRIBUICOES-llm-course.md). Cada A# pode apontar o módulo correspondente de lá; o texto da trilha continua nosso. **Não** executamos os labs 01–05/07–12 desse fork neste PR.

## O que vem depois deste PR

Próximos esqueletos: **A0** (bancada), depois **A3 → A4 → A5** (treino e SFT, que A8/A9/A10 declararam ausentes), **A6** (LoRA de produção), **A7** (raciocínio), **A12** (capstone). Ver os READMEs de cada pasta.
