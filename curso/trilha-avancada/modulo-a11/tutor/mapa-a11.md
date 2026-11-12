# Mapa de subhabilidades — A11 (MoE, quantização, inferência)

**Tema:** Mixture-of-Experts, PTQ/QAT e KV cache  
**Fontes (apenas referência; não reproduzir texto longo):**
- Aula: `curso/trilha-avancada/modulo-a11/aula.md`
- Labs: `curso/trilha-avancada/modulo-a11/lab/`
- Checkpoint: `curso/trilha-avancada/modulo-a11/checkpoint-ca11.md`
- Tronco citado, não copiado: M08 (MoE ≠ multiagente), M09 (LoRA / NF4 / harness)
- A2 citado: FFN denso, GQA, máscara causal
- Licença da trilha: pendente — [`LICENSE-PENDENTE.md`](../../LICENSE-PENDENTE.md). Este mapa parafraseia tópicos.

**Como usar:** cole `tutor/tutor-socratico-ptbr.md` **e** este mapa no assistente. Os níveis 0–5 são do tutor; **não** substituem CA11. O tutor **não** deve revelar `gabarito-instrutor/` nem inventar PPL, L1 ou speedup.

**Ordem sugerida de foco:** A → B → C → D → E → F.

A3, A5 e A6 **não** foram publicados. Não trate MiniGPT, SFT da trilha ou LoRA-em-expert como pré-requisito feito. CA11.3 não se cobra.

---

## Prompt de início (pronto para colar)

```
Use o tutor socrático com este mapa do A11 (MoE, quantização, inferência eficiente).
Siga a instrução do tutor (método socrático, diagnóstico sem ensinar, uma pergunta por vez, níveis 0–5 rigorosos).
Este mapa define as subhabilidades. É prática opcional: níveis do tutor não contam como nota nem substituem CA11.
Não entregue gabaritos de checkpoint nem invente resultados de laboratório; quando pedir evidência de lab, peça o ca11.json que eu produzi.
A3/A5/A6 não existem nesta trilha ainda: MoE é camada avulsa; PTQ é no SmolLM2; LoRA-MoE não foi medido.
Comece pelo diagnóstico e mostre o mapa inicial.
```

*(Cole também o arquivo `tutor-socratico-ptbr.md` na mesma mensagem, ou antes.)*

---

## Subhabilidades

### A. Router, top-*k* e o que não calcula

- **O que é domínio 4/5:** escrever `y = Σ_{i ∈ top-k} g_i E_i(x)` com gates no softmax *restrito* ao top-*k*; dizer que o expert fora do top-*k* não entra na soma nem no FLOP daquele token.
- **Ideias de perguntas diagnósticas (abertas; sem respostas aqui):**
  1. Se só existisse softmax cheio sem `topk`, o que deixaria de ser esparso?
  2. Gates no top-*k* e probs no softmax de *N* são o mesmo vetor? Por que (não)?
  3. No exemplo 2×3 da aula, qual expert *não* roda? O que aconteceria com `y` se você zerasse os pesos dele?
  4. Atenção (Q/K/V) no Granite é MoE ou densa?
  5. “MoE é um time de agentes” — o que essa frase acerta (especialização *possível*) e o que erra (ferramenta, diálogo, ReAct)?
- **Caso-limite (nível 5):** alguém soma os 32 experts e chama isso de “custo de inferência do Granite 1B-A400M”. O que se perde, e que campo da config você pediria?
- **Seção-fonte:** aula.md §§1–2; `lab/moe_brinquedo.py`; Shazeer 2017.
- **Prepara para:** **CA11.1** (exemplo_aula, totais vs ativos).

### B. Aux loss e colapso

- **O que é domínio 4/5:** escrever `L_aux = N · Σ f_i P_i`; interpretar `f` (despacho) vs `P` (prob média); prever histograma com expert 0 viciado sem α.
- **Ideias de perguntas diagnósticas:**
  1. Se `f = [1,0,…,0]`, o que acontece com o gradiente dos outros experts na *tarefa*?
  2. Por que a fórmula multiplica por *N*?
  3. Com *k*=2, `Σ f` vale 1 ou 2 neste lab, e por quê?
  4. Aux pode *piorar* o MSE da tarefa. Isso invalida o balanceamento?
  5. Switch usa *k*=1. O que muda na história do colapso, não na fórmula?
- **Caso-limite (nível 5):** o aluno remove `vies_expert0` “para ficar mais realista” e o colapso some. Como conduzir de volta ao critério do JSON sem entregar o valor 2.5?
- **Seção-fonte:** aula.md §3; Fedus 2101.03961; CA11.1.
- **Prepara para:** **CA11.1** (flags colapso / equilíbrio).

### C. Config de um MoE real

- **O que é domínio 4/5:** ler `num_local_experts` vs `num_experts_per_tok`; contrastar 1,3B totais / 400M ativos; saber que OLMoE 7B nesta CPU é leitura.
- **Ideias de perguntas diagnósticas:**
  1. 8/32 é fração de quê — parâmetros totais ou só do MLP?
  2. Por que `intermediate_size=512` no Granite não é 4×1024?
  3. Se `status=nao_coube`, o que ainda dá para avaliar no checkpoint?
  4. L1(Auto, Saúde) < L1(Auto, permutação de Saúde): especialização *falhou* ou a amostra é pequena?
  5. OLMoE 64×8 vs Granite 32×8: o que é mais *fino* (granular)?
- **Caso-limite (nível 5):** o aluno cola um heatmap de Twitter do Mixtral 8×7B como se fosse o Granite 1B. Que evidência você exige do `modelo` no JSON?
- **Seção-fonte:** aula.md §4; `inspecionar_moe.py`; CA11.2.
- **Prepara para:** **CA11.2**.

### D. PTQ vs QAT e bits

- **O que é domínio 4/5:** situar PTQ *depois* e QAT *durante* (STE); INT8 dinâmico CPU vs INT4 fake-quant (qualidade ≠ velocidade); não inventar GGUF.
- **Ideias de perguntas diagnósticas:**
  1. O `round` tem derivada zero. Como o QAT ainda treina?
  2. Por que INT4 neste lab não deve ficar *mais rápido*?
  2b. O JSON tem `int8_dinamico` e `int8_dinamico_sem_lm_head`. Qual pergunta você faz se o aluno comparar o primeiro com o INT4 fake e concluir que “8 bits perdem de 4”?
  3. NF4 do M09 é PTQ, QAT ou treino em pesos já quantizados (QLoRA)?
  4. PPL neste corpus curto é comparável à WikiText-2? Por quê (não)?
  5. `quantize_dynamic` avisou deprecated. Isso zera o lab ou é nota de API?
- **Caso-limite (nível 5):** PPL INT4 < PPL fp32 no JSON do aluno. Como pedir verificação (semente, corpus, fake-quant copiado errado) sem acusar fraude de cara?
- **Seção-fonte:** aula.md §§5–6; Jacob 1712.05877; `ptq.py`, `qat.py`.
- **Prepara para:** **CA11.4**, **CA11.5**.

### E. KV cache

- **O que é domínio 4/5:** desenhar que `K,V` do prefixo não mudam; ligar à máscara causal do A2; distinguir prova de *igualdade* e prova de *tempo*.
- **Ideias de perguntas diagnósticas:**
  1. Na geração do 5º token, quais K você reusa?
  2. GQA reduz o cache em que fator, olhando `n_kv_heads`?
  3. `greedy_ids_iguais=true` prova speedup? O que prova?
  4. Se `use_cache=False` sair *mais rápido* em 8 tokens na CPU, o que você pergunta antes de chamar bug?
  5. Quantizar pesos INT8 quantiza o KV cache?
- **Caso-limite (nível 5):** o aluno implementa cache mas esquece a máscara no passo novo e o Δ explode só na última posição. Que print do JSON pede?
- **Seção-fonte:** aula.md §7; `kv_cache.py`; CA11.6.
- **Prepara para:** **CA11.6** (Δ < 1e-5).

### F. Batching e serving (leitura honesta)

- **O que é domínio 4/5:** contrastar batch estático (lab 1/4/8) com continuous batching; citar PagedAttention como *ideia*, sem número de throughput inventado.
- **Ideias de perguntas diagnósticas:**
  1. Tokens/s no forward batch=8 é latência de um usuário?
  2. Por que KV de tamanhos diferentes quebra o batch denso ingênuo?
  3. O que o campo `nao_calibrado_cpu` está te proibindo de escrever no relatório?
  4. Ollama no M09 já fazia quantização. Qual pergunta nova o A11 te deixa fazer ao servidor?
  5. CA11.3 não rodou. Que frase honesta cabe no parágrafo — e qual não cabe?
- **Caso-limite (nível 5):** o aluno entrega “vLLM 2–4×” copiado do abstract do paper. Como redirecionar para o JSON sem recitar Kwon et al.?
- **Seção-fonte:** aula.md §8; Kwon 2309.06180; CA11.6 servidores.
- **Prepara para:** **CA11** parágrafo de honestidade; futuro A8 não depende disto.

---

## Notas para o tutor (e para o aluno)

- A1, A3, A5, A6 não publicados: não cobre BPE, MiniGPT, SFT da trilha nem LoRA de produção.
- Não execute download de Granite/SmolLM2 no lugar do aluno; peça o `ca11.json`.
- Domínio-alvo padrão: **4/5** em A–F. Nível 5 é opcional.
- Frases Amplitude do lab são sintéticas (`Ana Souza` / `ABC-1D23`); não peça os JSONL do M09.
- T4, vLLM, GGUF, OLMoE 7B: se o JSON diz `nao_calibrado`, o tutor **não** completa com um número “típico”.
