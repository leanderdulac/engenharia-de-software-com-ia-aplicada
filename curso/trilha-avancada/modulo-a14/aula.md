# A14 — Medindo generalização na prática

Trilha avançada, **opcional extra** (~4 h). **Fora** das 78 h de A0–A12, das +4 h do A13 e das 240 h de M01–M09. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca14.md`](./checkpoint-ca14.md). Sem gabarito nesta aula. Pré-requisito: **A5**. A13 recomendado (bound VC vácuo).

O A13 mostrou que o certificado de 1971, plugado no LoRA do A5, **não informa**: o termo é `inf`. Isso não autoriza chutar o erro em produção. Autoriza **medir**. Hold-out, k-fold, intervalo de confiança, vazamento. Ao final:

1. contrastar erro de treino com o que o cliente vê;
2. montar um hold-out que o treino não reescreve — e ver o lab **otimizar** a acc quando você vaza;
3. ler a variabilidade do k-fold no JSON;
4. colocar IC Wilson e bootstrap em cima dos números **já publicados** do A5 (n=2), do A13 (n=6) e do A7 (n=8) — e admitir que n=2 quase não fala;
5. traçar complexidade (polinômio, k-NN) e uma regularização ridge;
6. anotar double descent como ponte para redes grandes, **sem** copiar figura de paper.

Nada disto entra nas 240 h. Números saem do seu `ca14.json`.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| PDF do livro Lindholm et al. | **não baixado, não commitado**. Só citação em [`../leituras.md`](../leituras.md). A aula **não** traduz nem parafraseia o livro. |
| Figuras Belkin / Nakkiran | **não reproduzidas**. Lab próprio com features aleatórias. |
| A5 n_eval | **2** no JSON de autoria (1 acerto). n=6 é o hold-out do **A13**, mais uma linha pedagógica “se A5 tivesse n=6”. |
| T4 / IC de LLM em T4 | `nao_calibrado` |

---

## 1. Dois erros, não um

Treino minimiza o que você **vê**. Produção cobra o que você **não viu**. Chame o primeiro de \(R_{\mathrm{emp}}\) (já no A13) e o segundo de risco em produção: a média da perda num ponto novo, da mesma fonte, depois do deploy.

Se a fonte mudou (placa de outro país, JSONL de outro produto), nem o hold-out fala. Esta aula assume i.i.d. com a produção — a mesma hipótese frágil do A5 com 4 diálogos.

O A5: \(R_{\mathrm{emp}}=0\) (acc 1,00, n=4) e hold-out 0,50 (n=2). O bound VC não cobre o buraco. O buraco continua lá. A pergunta prática vira: *com que precisão o 0,50 estima o risco verdadeiro — e o 0,50 estava limpo?*

---

## 2. Hold-out e os jeitos de vazar

Separe um conjunto **antes** de escolher modelo, hiperparâmetro e pré-processamento. Cada olhada no teste gasta o teste. Três furos que o lab mede ou nomeia:

**Estatística / seleção no conjunto inteiro.** `SelectKBest.fit(X, y)` com o y do teste escolhe features que *já viram* o futuro. O A14.2 compara isso com selecionar **só no treino**. Se a primeira acc for maior, você comprou um número otimista. Em LLM o primo é escolher o prompt ou o corte de similaridade no conjunto que depois vira eval. `StandardScaler` no X inteiro é o primo mais fraco da mesma família.

**Duplicata no teste.** Copiar linhas do treino para o eval. O A14.3 faz isso de propósito. Em LLM: o mesmo diálogo no SFT e no harness; o mesmo item de MMLU no pré-treino. “Dedup” e “contaminação de benchmark” são nomes da mesma falha: o teste deixou de ser novo. O M09 trata eval gate; **não** editamos o M09 — apontamos o instinto.

**Teste que o agente edita.** A caixa `/teamwork` (opcional) já disse: suíte original, não modificada. Aqui o analogato é: o arquivo de eval não entra no `fit`.

k-fold (A14.4) não cura vazamento. Embaralha a mesma massa. Serve para ver **variância da estimativa** quando n é curto: cinco números, não um.

---

## 3. n pequeno: o IC é o certificado que você ainda tem

Acurácia é média de Bernoulli. Com k acertos em n provas, o intervalo de **Wilson** (95%) e o **bootstrap** percentil da sequência 0/1 são duas contas honestas. Não são VC. Não precisam da dimensão da classe. Precisam de i.i.d. e de o teste não ter vazado.

O lab **não** relê `saidas/` gitignoradas. Pluga os inteiros já publicados:

| Origem | k/n | acc |
| --- | ---: | ---: |
| A5 eval (autoria) | 1/2 | 0,50 |
| A13 Zhang SVM RBF eval | 3/6 | 0,50 |
| A7 acc_direto | 3/8 | 0,375 |
| Linha pedagógica (A5 **não** mediu isto) | 3/6 | 0,50 |

n=2: o intervalo cobre quase tudo. “acc=0,50” no A5 é um ponto, não uma medição estreita. n=6 ainda é largo — por isso o A13 não podia transformar 0,50 em teoria. n=8 no A7 continua largo: 0,375 de CoT vs direto **não** decide campeão.

Se o JSON marcar `vacuo_pratico=true` (largura Wilson ≥ 0,5), trate o ponto como **indício**, não como gate de promoção. O A12 já recusou INT8 com ppl; aqui recuse certeza com n=2.

---

## 4. Viés, variância, complexidade — o que o sklearn mostra hoje

Classe pobre demais: treino e teste ruins (viés). Classe rica demais: treino excelente, teste pior (variância). O A14.5 treina polinômio em um seno ruidoso (graus 1…16) e k-NN (k=1,3,9,21). k=1 decora o treino; k grande alisa. Ridge no mesmo polinômio alto puxa o teste de volta. Nada disto é a VC do LoRA. É o desenho clássico **medido**, para você não falar “overfit” sem curva.

Regularização (A14.5 ridge) é o botão operacional quando você **não** tem bound: penalize \(\lVert w\rVert\) e escolha o α no treino interno, nunca no teste final.

---

## 5. Double descent, em uma nota

Redes que interpolam o treino (A5, Zhang no A13) às vezes **melhoram** o teste quando a capacidade passa do ponto de interpolação. Belkin, Hsu, Ma & Mandal, PNAS 2019 ([arXiv 1812.11118](https://arxiv.org/abs/1812.11118)); Nakkiran et al., 2019 ([arXiv 1912.02292](https://arxiv.org/abs/1912.02292)). **Não** copiamos as figuras.

O A14.6 monta um min-norm em features aleatórias e registra se o MSE de teste sobe perto de p≈n e se desce depois. Se não descer nesta semente, o JSON diz isso. Double descent **não** é garantia de que o SmolLM2 generaliza; é o nome do regime em que o U clássico não conta a história toda.

---

## 6. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| Wilson A5 1/2 | **[0,095 ; 0,905]** largura 0,81 (`vacuo_pratico`) |
| Wilson n=6 (A13 Zhang e linha pedagógica) | **[0,188 ; 0,812]** largura 0,62 |
| Wilson A7 3/8 | **[0,137 ; 0,694]** largura 0,56 |
| SelectKBest no conjunto inteiro | acc **0,778 vs 0,704** (Δ **+0,074** otimista) |
| duplicata no teste (k-NN 1) | **0,600 → 0,791** (Δ **+0,191**) |
| 5-fold n=80 | média **0,788** sd **0,130** (0,625–0,938) |
| poly mse eval graus 1/4/16 | **0,390 / 0,187 / 1,247** (U; treino só cai) |
| k-NN acc treino k=1 vs 21 | **1,00 vs 0,79** |
| ridge α=0,01 vs OLS grau 14 | eval **0,173 vs 0,515** |
| pico interpolação | **p=40 = n**; depois desceu (`desceu_depois_do_pico=true`) |

---

## 7. O que fazer agora

1. `python modulo-a14/lab/lab_a14.py`
2. CA14 com o JSON **seu**: um parágrafo ligando o IC do A5 (n=2) ao bound vácuo do A13.
3. Não escreva que o livro Lindholm “foi seguido nesta aula”. Não foi. Leitura opcional: [`../leituras.md`](../leituras.md).
