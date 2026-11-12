# Mapa de subhabilidades — A2 (bloco Transformer)

**Tema:** O bloco Transformer, peça por peça  
**Fontes (apenas referência; não reproduzir texto longo):**
- Aula: `curso/trilha-avancada/modulo-a2/aula.md`
- Labs: `curso/trilha-avancada/modulo-a2/lab/`
- Checkpoint: `curso/trilha-avancada/modulo-a2/checkpoint-ca2.md`
- Tronco citado, não copiado: M01 (amostragem), M09 (LoRA em q/v)
- Licença da trilha: pendente — [`LICENSE-PENDENTE.md`](../../LICENSE-PENDENTE.md). Este mapa parafraseia tópicos.

**Como usar:** cole `tutor/tutor-socratico-ptbr.md` **e** este mapa no assistente. Os níveis 0–5 são do tutor; **não** substituem CA2. O tutor **não** deve revelar `gabarito-instrutor/` nem inventar Δ do lab.

**Ordem sugerida de foco:** A → B → C → D → E → F.

---

## Prompt de início (pronto para colar)

```
Use o tutor socrático com este mapa do A2 (bloco Transformer).
Siga a instrução do tutor (método socrático, diagnóstico sem ensinar, uma pergunta por vez, níveis 0–5 rigorosos).
Este mapa define as subhabilidades. É prática opcional: níveis do tutor não contam como nota nem substituem CA2.1/CA2.2.
Não entregue gabaritos de checkpoint nem invente resultados de laboratório; quando pedir evidência de lab, peça o ca2.json que eu produzi.
Comece pelo diagnóstico e mostre o mapa inicial.
```

*(Cole também o arquivo `tutor-socratico-ptbr.md` na mesma mensagem, ou antes.)*

---

## Subhabilidades

### A. Q, K, V e a raiz de d_k

- **O que é domínio 4/5:** escrever, com as próprias palavras, que Q/K/V são três projeções lineares da mesma sequência; completar a fórmula `softmax(QKᵀ/√d_k)V`; justificar a raiz pela variância do produto interno (sem recitar o paper).
- **Ideias de perguntas diagnósticas (abertas; sem respostas aqui):**
  1. Se só existisse `x W_V`, o que o bloco deixaria de fazer entre posições?
  2. Por que três matrizes e não uma?
  3. O que explode no softmax se você *omitir* `√d_k` com `d_k` grande?
  4. No M09, o que `q_proj` e `v_proj` são, neste vocabulário?
  5. No exemplo 2×2 da aula, *sem olhar o arquivo*, qual linha de `QKᵀ` corresponde à posição 0?
- **Caso-limite (nível 5):** alguém diz que “atenção é cosine similarity”. O que essa frase acerta, o que erra (escala, softmax, V), e como você corrigiria sem entregar o tensor da aula?
- **Seção-fonte:** aula.md §§2–3; `lab/atencao.py`; Vaswani §3.2.1.
- **Prepara para:** **CA2.1** (igualdade com SDPA).

### B. Máscara causal

- **O que é domínio 4/5:** desenhar o triângulo “posição i não lê j>i”; explicar o vazamento de gabarito no treino se a máscara cair; descrever o teste de *mudar só o último token*.
- **Ideias de perguntas diagnósticas:**
  1. Na geração do quarto token, quais posições de chave são legais?
  2. Qual o truque numérico para um score “proibido” não ganhar massa no softmax?
  3. Padding e causal são a mesma máscara? Por quê (não)?
  4. Se o teste causal falhar só na última posição, isso é bug ou esperado?
  5. Encoder BERT usaria essa máscara? Que problema de produto isso criaria num chat?
- **Caso-limite (nível 5):** um aluno “conserta” NaNs no softmax enchendo a máscara com 0 em vez de −∞. Que artefato isso introduz no mapa, e que evidência você pediria no JSON?
- **Seção-fonte:** aula.md §4; `prova_que_o_futuro_nao_vaza`; CA2.1.
- **Prepara para:** **CA2.1** (causal_ok).

### C. Multi-cabeça e GQA

- **O que é domínio 4/5:** explicar concatenar `h` cabeças + `W_O`; ler `num_attention_heads` vs `num_key_value_heads` numa config; dizer em uma frase por que `k_proj` pode ser mais estreito que `q_proj`.
- **Ideias de perguntas diagnósticas:**
  1. Se `d=576` e `h=9`, quanto vale `d_h`?
  2. O que GQA reutiliza, e o que continua “por cabeça”?
  3. Por que o mapa de atenção no lab tem shape `(1, 9, S, S)` e não `(1, 3, S, S)` no SmolLM2?
  4. LoRA só em `q,v` deixa K de fora — que hipótese isso testa (sem pedir o lab do A6)?
  5. Multi-query (`h_kv=1`) é um extremo de quê?
- **Caso-limite (nível 5):** alguém soma as 9 cabeças do mapa e chama isso de “atenção do modelo”. O que se perde, e como pedir evidência de *uma* cabeça?
- **Seção-fonte:** aula.md §5; `ler_config`; Ainslie 2023.
- **Prepara para:** **CA2.2** (config / GQA).

### D. Posição: senoide vs RoPE

- **O que é domínio 4/5:** contrastar “somar um vetor de posição” com “girar Q e K”; saber que V não gira; ler `rope_theta` sem fingir que é o 10000 do paper.
- **Ideias de perguntas diagnósticas:**
  1. Sem nenhum sinal de posição, o que o softmax não consegue distinguir?
  2. RoPE age em Q, em K, em V ou nos três?
  3. O MiniDecoder do lab usa RoPE ou senoide? Por que essa escolha didática?
  4. O que `rope_interleaved=false` muda na rotação (ideia, não a fórmula completa)?
  5. Alongar contexto só aumentando `max_position_embeddings` na config resolve RoPE? Que suspeita você teria?
- **Caso-limite (nível 5):** a reconstrução do bloco dá Δ grande *só* se você pular RoPE. Como o tutor conduz o aluno a isolar isso pedindo o JSON, sem colar `aplicar_rope`?
- **Seção-fonte:** aula.md §6; `lab/posicional.py`; Su et al. 2021.
- **Prepara para:** **CA2.2** (reconstrução).

### E. Resíduo + norma (e pré vs pós)

- **O que é domínio 4/5:** escrever o bloco pré-norma em duas linhas; contrastar LayerNorm (centra) e RMSNorm (não centra); prever o que acontece se comparar pós-norma com o `hidden_state` do HF.
- **Ideias de perguntas diagnósticas:**
  1. Se a atenção devolver ~0, o que sai do bloco?
  2. LayerNorm em `[1,2,3]`: a coordenada do meio, depois da norma, vai a que valor (ordem de grandeza / sinal), e por quê?
  3. RMSNorm precisa de `β` (bias) no Llama?
  4. Pré-norma: a norma vê `x` ou `x+f(x)`?
  5. Quantas RMSNorm há *por bloco* no SmolLM2, além da norma final do modelo?
- **Caso-limite (nível 5):** Δ=0.4 no bloco, testes de atenção isolada verdes. Onde você olharia primeiro (ordem norma/resíduo vs bug de GQA), e que print do JSON pediria?
- **Seção-fonte:** aula.md §§7–8; `lab/normas.py`; `lab/bloco.py`.
- **Prepara para:** **CA2.2** (diff_max do bloco).

### F. Contagem de parâmetros e fluxo no LLM

- **O que é domínio 4/5:** montar a tabela embedding / atenção / FFN / norma / lm_head sem contar peso amarrado duas vezes; situar decoder-only vs encoder-decoder; ligar o bloco à amostragem do M01.
- **Ideias de perguntas diagnósticas:**
  1. Se `tie_word_embeddings=true`, `lm_head` aparece na soma do `named_parameters`?
  2. Onde está a maior fatia em um modelo de 0,1B — embedding, atenção ou MLP? (peça o JSON, não chute)
  3. Cross-attention existe no SmolLM2?
  4. `hidden_states` tem um tensor a mais que o número de camadas. O que é o índice 0?
  5. Por que `eager` e não SDPA quando se pede o mapa?
- **Caso-limite (nível 5):** o aluno entrega `num_parameters()` mas a soma dos baldes difere 50% (tirou o embedding duas vezes). Como conduzir a correção pedindo `id(p)` sem abrir o gabarito?
- **Seção-fonte:** aula.md §§9–10; `contar_parametros`; CA2.2.
- **Prepara para:** **CA2.2** (erro_relativo ≤ 0,1%).

---

## Notas para o tutor (e para o aluno)

- A1 ainda não foi publicado: não cobre BPE nem top-p como se o aluno tivesse feito A1.
- Não execute download de modelo no lugar do aluno; peça o `ca2.json`.
- Domínio-alvo padrão: **4/5** em A–F. Nível 5 é opcional.
- Frase Amplitude do lab é sintética (`Ana Souza` / `ABC-1D23`); não peça os JSONL do M09.
