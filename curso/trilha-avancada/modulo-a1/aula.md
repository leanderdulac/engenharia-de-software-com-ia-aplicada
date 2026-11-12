# A1 — Por dentro do LLM: tokens, logits e amostragem

Trilha avançada, **opcional**. Guia da pasta: [`README.md`](./README.md). Checkpoint: [`checkpoint-ca1.md`](./checkpoint-ca1.md). Esta aula **não** contém gabarito de CA1.

No M01 você *sentiu* temperature e top-K nos sliders do Chrome. No A2 (já publicado) o bloco produz um vetor em `R^{|V|}`. Aqui o meio: o que é um token, quanto ele custa em português, como logits viram probabilidade, e como o laço escolhe o próximo id. Ao final você deve conseguir:

1. contrastar n-grama, rede recorrente e foundation model sem recitar marketing;
2. explicar BPE (Sennrich 2016) e por que PT costuma gastar mais tokens que EN;
3. desenhar o laço autorregressivo e a janela de contexto;
4. escrever softmax com temperatura, top-k, top-p e greedy *sem* chamar `generate`;
5. dizer o que o treino faz em paralelo e o que a geração faz em série.

Nada disto entra nas 240 h. Números de tokenização e entropia **não** se copiam da aula: saem do seu `ca1.json`.

---

## 0. Ponte com o M01 (não duplicar)

O tronco já cobre, e esta aula **aponta** em vez de reescrever:

| Já está no M01 | O que o A1 acrescenta |
| --- | --- |
| Seção “LLM: amostragem, não oráculo” em [`curso/conteudo/modulo-01/aula.md`](../../../conteudo/modulo-01/aula.md) | a fórmula `p = softmax(z / T)` e a entropia vs T |
| Lab [`exemplo-04-webai02-temperature-and-topK`](../../../../modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-04-webai02-temperature-and-topK/) (sliders, Prompt API) | o mesmo knob, agora em PyTorch, conferido contra `transformers` |
| Glossário: temperature / top-K | **top-p** (núcleo, Holtzman 2019) — **não** é aula no tronco |
| Embeddings de *sentença* no Neo4j (`exemplo-12` / `exemplo-13`) | embedding de *token*: uma linha da tabela `E` |
| “o LLM amostra o próximo token” | o laço, a janela, a diferença treino / forward / geração |

Se você ainda não fez o exemplo 04 com a **mesma** pergunta em T=0 e T=1, faça. O A1 não substitui aquele sentimento; ele mostra a conta por trás do slider. A0 (bancada) ainda é esqueleto: o JSON traz o ambiente como no A2, sem `bancada.json`.

---

## 1. Uma linha do tempo, sem nostalgia

Modelos de linguagem predizem o próximo símbolo dado o prefixo.

- **n-gramas** (Shannon, contagem): `P(w_t | w_{t-n+1}…w_{t-1})` numa tabela. Explode em esparsidade; “sinistro na Amplitude” nunca visto some.
- **Redes recorrentes / LSTM**: um estado esconde o prefixo. Treina com backprop no tempo; esquece o começo da frase longa.
- **Transformer decoder-only** (A2): cada posição lê o passado com atenção causal. Escala. É o que esta trilha abre.
- **Foundation model**: um treino em texto amplo (e às vezes código, áudio, imagem) que depois se *adapta* — SFT, LoRA, DPO, GRPO, destilação. O M09 já decide *se* adaptar; A3–A10 ensinam *como*. GPT-2 (Radford et al. 2019) popularizou o decoder-only gerativo; GPT-3 (Brown et al. 2020) mostrou few-shot em escala. O lab usa SmolLM2-135M (Apache-2.0), não esses pesos.

Não existe “o” foundation model. Existe um *checkpoint* com tokenizer, janela, licença e um cartão. Sem o cartão, você não destila (A10) nem serve (A11).

---

## 2. Tokenização: BPE e o custo PT vs EN

O modelo não lê letras. Lê **ids** inteiros num vocabulário fixo `|V|`. SmolLM2: `|V| = 49 152`. Qwen2.5-0.5B: `|V| = 151 643`. Caracteres: 256 (baseline do lab; não é um LLM).

Palavra aberta + vocabulário fechado: Sennrich, Haddow e Birch (2016, [1508.07909](https://arxiv.org/abs/1508.07909)) adaptam **byte pair encoding** (Gage 1994) para juntar pares de símbolos frequentes até caber em `|V|`. Palavras comuns viram um token; raras viram pedaços. No lab, `Segurado` vira `Seg` + `ur` + `ado` nos dois tokenizers HF — não é um átomo.

O `Ġ` no print é o espaço à esquerda (byte-level BPE). Não é um glifo do português; é como o tokenizer marca “começou palavra”.

**Custo.** APIs cobram tokens, não caracteres. Tokenizers treinados em inglês deixam o português mais fatiado. Nesta VM, par quase paralelo “sinistro / claim”:

| Tokenizer | PT | EN | razão PT/EN |
| --- | ---: | ---: | ---: |
| SmolLM2 | 21 | 15 | **1,40** |
| Qwen2.5-0.5B (só tokenizer) | 19 | 14 | **1,36** |
| caracteres | 60 | 58 | 1,03 |

A frase da soma (“doze mais sete” vs “twelve plus seven”) foi a 1,50 no SmolLM2. Isso **não** é lei: é *esta* tabela. Se o seu JSON der 1,1, o parágrafo cita 1,1. Copiar 1,40 sem arquivo zera.

Consequência de produto: o mesmo *significado* em PT pode estourar a janela antes, custar mais, e entrar menos contexto no RAG do M01. A janela do SmolLM2 nesta config é `max_position_embeddings = 8192` (campo no JSON). Estourar a janela não “resume”: corta ou recusa.

---

## 3. Embedding de token ≠ embedding de sentença

Cada id `t` indexa a linha `E[t] ∈ R^d`. SmolLM2: `d = 576`, `tie_word_embeddings=true` (a cabeça de predição reusa `E` — A2 já contou isso). Uma sentença de 21 tokens vira uma matriz `21 × 576`, não um vetor só. O vetor único do Neo4j no M01 é *outra* função (média, CLS, modelo de sentença). Misturar os dois nomes na CA1 é erro de conceito, não de aritmética.

Posição ainda não entrou: sem RoPE/senoide, “Ana” no começo e “Ana” no fim começam iguais. Isso é A2 §6.

---

## 4. Geração autorregressiva

Um passo:

```text
prefixo ids → modelo → logits z ∈ R^{|V|} → amostrador → id t+1 → concatena
```

Oito passos no lab = oito forwards. KV cache (A11) evita recomputar o prefixo; o A1 **não** implementa cache de propósito.

**Treino** (A3, esqueleto): o mesmo prefixo de comprimento S produz S−1 logits **em paralelo**, com máscara causal. A perda é CE no próximo token. Teacher forcing: o modelo vê o ouro na posição `t` mesmo se teria errado em `t−1`.

**Forward / inferência de um passo:** `model(ids)` devolve logits de todas as posições. Útil para destilação (A10) e para o *último* logit da geração.

**Geração:** série. Cada id amostrado condiciona o próximo. Erro no token 1 estraga o 8. Greedy neste 135M para `2+2=` saiu `"4\n\nA = 1\n"` — o primeiro inteiro está certo; o resto é o modelo continuando. O A10 já mostrou o mesmo lixo no professor 360M.

---

## 5. Logits → softmax → temperatura

`z_i` é um score, não uma probabilidade. Softmax estável (lab):

```text
p_i = exp(z_i − max z) / Σ_j exp(z_j − max z)
```

Temperatura `T > 0`:

```text
p_i(T) = softmax(z / T)_i
```

`T < 1` afia (massa no argmax). `T > 1` achata. **Não existe T=0** na divisão; greedy é `argmax(z)`, o limite. O slider “0” do exemplo 04 é esse limite, não uma divisão por zero.

Nesta corrida, no último logit de `2+2=`, top-5 em T=1: `4` (0,47), `5` (0,17), `3` (0,10), `6` (0,08), `1` (0,03). Greedy pega `4`. Entropia `H = −Σ p log p` (nats):

| T | H | H / log\|V\| |
| ---: | ---: | ---: |
| 0,1 | 0,001 | ≈ 0 |
| 0,5 | 0,678 | 0,06 |
| 1,0 | 2,058 | 0,19 |
| 1,5 | 6,068 | 0,56 |
| 2,0 | 9,098 | 0,84 |

`log(49152) ≈ 10,80`. T=2 ainda não é uniforme; já está perto. O M01 pede para *sentir* T=0 vs T=1. Aqui você mede o achatamento.

---

## 6. Greedy, top-k, top-p

**Greedy:** `t = argmax z`. Determinístico. Repete. Holtzman et al. (2019, [1904.09751](https://arxiv.org/abs/1904.09751)) mostram degeneração em textos longos com maximização (beam). O lab só gera 8 tokens: o laço *bate* com `model.generate(do_sample=False)` (`greedy_ids_iguais=true`). Isso é o teste. Não é um ensaio de qualidade literária.

**Top-k** (Fan et al. 2018; o slider do M01): fica com os k maiores logits, o resto −∞, depois softmax. k fixo: às vezes largo demais (cauda lixo), às vezes estreito demais (corta um núcleo grande).

**Top-p / núcleo** (Holtzman §3.1): menor conjunto cuja massa cumulativa ≥ p. O tamanho *varia* com o passo. O lab replica o warper do `transformers` 5.22 (ordena logits crescentes, corta `cumsum ≤ 1−p`, guarda ≥ 1 token). Δ vs HF nesta VM: **0** nos três (T, k, p).

Ordem usual: temperatura → top-k → top-p → softmax → amostra. min-p (bonus, não é CA): corta tokens com `p < min_p · p_max`. O lab não o implementa.

---

## 7. O que o lab mediu, em uma frase

A1.1: PT gasta ~1,4× os tokens do EN neste par, nos dois BPE; caracteres não veem o efeito. A1.2: o laço greedy reproduz `generate`; warpers batem com Δ=0; entropia sobe com T. T4 / Prompt API / custo por 1k de provedor = **não calibrado** (A0 esqueleto, CPU sem CUDA).

---

## 8. O que fazer agora

1. Relê a seção do M01 e, se faltar, o exemplo 04. Não cole o HTML aqui.
2. `python modulo-a1/lab/lab_a1.py`
3. CA1 com o JSON **seu**. A razão PT/EN e o texto greedy saem de lá.
4. Opcional: [`tutor/mapa-a1.md`](./tutor/mapa-a1.md).
5. A2 continua sendo o bloco que *produz* estes logits — agora com o sampler visível.

Não copie 1,40 nem `"4\\n\\nA = 1\\n"` desta CPU. Outro tokenizer, outro prompt, outros números.
