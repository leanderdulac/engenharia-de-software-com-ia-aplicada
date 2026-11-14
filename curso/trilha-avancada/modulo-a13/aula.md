# A13 — Generalização clássica: Vapnik, VC e SVM — e onde ela falha em LLMs

Trilha avançada, **opcional**, **fora** das 78 h de A0–A12 e das 240 h de M01–M09. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca13.md`](./checkpoint-ca13.md). Sem gabarito nesta aula. Pré-requisito: **A5**.

No A5 o LoRA interpolou 4 diálogos (acc treino **1,00**) e errou metade do hold-out (acc eval **0,50**). Isso não é um bug do collator. É a pergunta que Vapnik e Chervonenkis formulam em 1971: a frequência empírica converge **uniformemente** à probabilidade, na classe de hipóteses que você deixou o algoritmo escolher? Ao final:

1. estilhaçar 3 pontos no plano e ver o XOR de 4 falhar;
2. medir margem e nº de vetores de suporte em função de C;
3. comparar SVM linear, SVM RBF e regressão logística sobre frases do domínio (sinistro / segurado / placa vs. fora);
4. embaralhar rótulos e ver treino perfeito com teste no acaso — o teste de Zhang;
5. ligar os números do A5 ao termo VC e dizer, com o JSON na mão, que **VC não é a teoria de generalização dos LLMs**.

Nada disto entra nas 240 h. Números saem do seu `ca13.json`.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| VC-dimensão do LoRA / SmolLM2 | **não calculada**. O lab pluga `h_proxy = 460 800` (params LoRA do A5) na fórmula clássica só para mostrar o bound **vácuo**. Isso não é a VC da rede. |
| CIFAR de Zhang et al. 2017 | **não reproduzido**. Espelho sklearn nas frases do domínio. |
| sentence-transformers | **não** está em `requirements.txt`. Encoder: mean-pool SmolLM2-135M; se falhar, TF-IDF declarado no JSON. |
| JSONL do M09 | **não lido**. Frases originais em `frases_dominio.py`. |
| T4 | `nao_calibrado` |

---

## Box: Vapnik, fatos com fonte

Só o que tem data e origem. O resto fica de fora.

- **1936.** Vladimir Naumovich Vapnik nasceu em 1936. Fonte: NEC C&C Prize 2013, *Citation* (“born in 1936”); Institute of Control Sciences (IPU RAN), biografia, data de acesso 2026-11-14 (6 de dezembro de 1936).
- **Tashkent.** Local de nascimento: Tashkent. Fonte: Wikidata [Q983367](https://www.wikidata.org/wiki/Q983367), acesso 2026-11-14; Wikipedia EN *Vladimir Vapnik*, acesso 2026-11-14. O PDF da NEC 2013 **não** menciona a cidade.
- **1958.** Mestrado na Universidade Estatal do Usbequistão, Samarcanda. Fonte: NEC C&C Prize 2013.
- **1964 / 1961–1990.** Doutorado em 1964 no Institute of Control Sciences, Moscou; permaneceu no instituto de 1961 a 1990. Fonte: NEC C&C Prize 2013.
- **Artigo de 1995.** Cortes & Vapnik, *Support-Vector Networks*, Machine Learning 20:273–297. **Received 15 May 1993 / Accepted 20 February 1995** — dateline do próprio artigo (Springer). DOI [10.1007/BF00994018](https://doi.org/10.1007/BF00994018).

Contagem de citações Google Scholar: **omitida** (não conferida nesta bancada com data de captura).

---

## 1. ERM — minimizar o erro que você vê

Dado um conjunto \(S = \{(x_i, y_i)\}_{i=1}^n\) i.i.d. de uma distribuição \(P\), o risco verdadeiro de uma hipótese \(f\) é \(R(f) = P(f(x) \neq y)\). Você **não** tem \(P\). Tem a média no treino:

\[
R_{\mathrm{emp}}(f) = \frac{1}{n}\sum_{i=1}^n \mathbf{1}[f(x_i) \neq y_i].
\]

*Empirical Risk Minimization* (ERM): escolha, numa classe \(\mathcal{F}\), a \(f\) que minimiza \(R_{\mathrm{emp}}\). No A5, 64 passos de LoRA empurraram a CE do assistant para ~0,05 e a acc de treino para 1,00. ERM fez o trabalho. A pergunta é se \(R_{\mathrm{emp}}\) ainda fala de \(R\).

---

## 2. Convergência uniforme: a pergunta de 1971

Para **uma** \(f\) fixa, a lei dos grandes números diz que \(R_{\mathrm{emp}}(f) \to R(f)\). O algoritmo **não** fixa \(f\) antes de ver \(S\): ele escolhe a que melhor cabe. Precisa de

\[
\sup_{f \in \mathcal{F}} \lvert R_{\mathrm{emp}}(f) - R(f) \rvert \to 0
\]

quando \(n \to \infty\). Isso é convergência **uniforme** na classe. Vapnik & Chervonenkis 1971 (DOI [10.1137/1116025](https://doi.org/10.1137/1116025)) caracterizam quando isso acontece, em termos da *growth function* da classe — quantas dicotomias \(\mathcal{F}\) realiza em \(n\) pontos.

Se a classe realiza **todas** as \(2^n\) rotulações, o supremo não some: sempre existe uma \(f\) que decora o treino e erra fora. ERM então não garante nada.

---

## 3. Dimensão VC via shattering

Uma classe \(\mathcal{F}\) **estilhaça** (*shatters*) um conjunto \(\{x_1,\ldots,x_h\}\) se, para **toda** rotulação \(y \in \{0,1\}^h\), existe \(f \in \mathcal{F}\) com \(f(x_i)=y_i\). A dimensão VC de \(\mathcal{F}\) é o maior \(h\) estilhaçável (0 se nenhum ponto é estilhaçável).

No plano, semirretos / hiperplanos lineares: 3 pontos **não colineares** são estilhaçáveis (as 8 dicotomias têm uma reta). 4 vértices de um quadrado **não**: o XOR — vértices opostos na mesma classe — não tem reta. O lab A13.1 mede isso com `SVC(kernel="linear", C=1e6)`: 8/8 no triângulo, XOR com acc de treino ≠ 1. Conclusão operacional: VC das retas em \(\mathbb{R}^2\) é 3.

VC não é “número de parâmetros”. Uma rede com milhões de pesos pode ter VC enorme; um SVM linear em 2D tem VC 3. O LoRA do A5 tem 460 800 parâmetros treináveis — isso **não** é a VC-dimensão da classe, e o lab recusa essa identificação.

---

## 4. O limite de generalização — e quando fica vazio

Uma forma típica (Vapnik 1999, IEEE TNN, DOI [10.1109/72.788640](https://doi.org/10.1109/72.788640); constantes variam conforme a derivação) é

\[
R(f) \le R_{\mathrm{emp}}(f) + \sqrt{\frac{h(\ln(2n/h)+1)+\ln(4/\delta)}{n}},
\]

com probabilidade ≥ \(1-\delta\), para \(h < n\). O segundo termo é o preço da capacidade. Três leituras honestas:

1. Se \(h \ge n\), a fórmula **nem está no regime** em que o logaritmo faz sentido. O lab devolve `inf` e marca `vacuo=true`.
2. Se o termo \(\varepsilon \ge 1\), o limite \(R \le R_{\mathrm{emp}}+\varepsilon\) não informa: risco já é ≤ 1. Bound **vácuo**.
3. No A5, \(n=4\). Mesmo plugando \(h=3\) (retas no plano), \(\varepsilon \ge 1\). Plugando o *proxy* 460 800, `inf`. O bound clássico **não fala** daquele SFT.

Isso não “refuta” Vapnik. Diz que a hipótese que o LoRA percorre é grande demais, e \(n\) é pequeno demais, para aquele certificado.

---

## 5. SRM — penalizar a capacidade, não só o treino

*Structural Risk Minimization*: aninhe classes \(\mathcal{F}_1 \subset \mathcal{F}_2 \subset \cdots\) de VC crescente e escolha o anel que minimiza \(R_{\mathrm{emp}} + \varepsilon(h,n)\). Não é “regularização L2” com outro nome: é um princípio de escolha de **modelo**. O SVM de margem máxima é uma realização concreta: entre os hiperplanos que separam, fique com o de menor \(\lVert w \rVert\) (maior margem), que controla uma medida de capacidade.

---

## 6. Margem máxima, vetores de suporte, kernel, C

**Margem.** Hiperplano \(w\cdot x + b = 0\). Com pontos em \(\{\pm 1\}\) e vinco \(|w\cdot x_i + b| \ge 1\), a margem geométrica é \(2/\lVert w \rVert\). Maximizar margem = minimizar \(\lVert w \rVert^2/2\) sujeito a classificar certo. Só os pontos no vinco — **vetores de suporte** — entram na expansão de \(w\). Os outros podem sair do treino que a solução não muda.

**Kernel** (Boser, Guyon & Vapnik 1992, DOI [10.1145/130385.130401](https://doi.org/10.1145/130385.130401)). O dual depende de produtos internos \(x_i\cdot x_j\). Troque por \(k(x_i,x_j)=\phi(x_i)\cdot\phi(x_j)\) e separe num espaço de features sem construir \(\phi\). RBF é o exemplo do lab.

**Soft margin** (Cortes & Vapnik 1995, DOI [10.1007/BF00994018](https://doi.org/10.1007/BF00994018)). Dados não separam. Folgas \(\xi_i \ge 0\); objetivo \(\lVert w \rVert^2/2 + C\sum\xi_i\). **C grande:** aproxima hard-margin, margem menor, menos paciência com erros. **C pequeno:** margem larga, mais vetores de suporte, mais violações. O lab A13.2 mede `n_sv` e \(2/\lVert w \rVert\) em blobs 2D que se tocam: C=0,01 vs C=100.

---

## 7. Zhang et al. 2017: redes decoram rótulos aleatórios

Zhang, Bengio, Hardt, Recht & Vinyals, *Understanding deep learning requires rethinking generalization*, ICLR 2017, arXiv [1611.03530](https://arxiv.org/abs/1611.03530). Experimento central: embaralhe os rótulos de treino de uma imagem. Uma convnet **ainda** chega a erro de treino ~0. O erro de teste, claro, fica no acaso. A classe de hipóteses é tão rica que ERM interpola **ruído**. O bound VC, com \(h\) da ordem dos parâmetros, já era vácuo em CIFAR; o paper mostrou o fenômeno na prática.

O lab A13.4 faz o espelho em CPU: TF-IDF das frases do domínio, `y` de treino permutado, SVM RBF e um MLP pequeno. Leia `acc_treino` vs `acc_eval` no JSON. Se treino = 1 e eval ~ acaso, você viu Zhang em 16 frases.

O A5 é o mesmo desenho em LLM: n=4, capacidade ≫ n, acc 1,00 / 0,50. Fabio no eval coloca a placa no campo `segurado` — memorizou o *formato*, não o vínculo nome↔placa.

---

## 8. VC **não** é a teoria de generalização dos LLMs

Diga isso sem rodeio.

1. O certificado 1971/1999 precisa de \(h \ll n\) (ou pelo menos \(h < n\) com \(\varepsilon < 1\)). LoRA no A5: 460 800 parâmetros, n=4. Bound vácuo.
2. Redes profundas interpolam rótulos aleatórios (Zhang 2017). Uma classe que estilhaça o treino **não** tem convergência uniforme útil.
3. LLMs generalizam *às vezes* com interpolação: o fenômeno que a teoria clássica trata como falha é o regime padrão de treino. Outras ferramentas (medidas de margem em NTK, compressão, estabilidade, *algorithmic* alignment, scaling laws) tentam explicar isso. Nenhuma delas é “a VC do GPT”.
4. Usar VC como discurso de marketing (“o modelo generaliza porque a teoria garante”) é falso neste regime. O lab existe para você **medir** o vazio, não para decorar o nome Vapnik.

O que *permanece* útil da escola: a **pergunta** (uniforme em quê?), a distinção ERM vs. SRM, e o SVM como algoritmo — não como certificado de LLM.

---

## 9. Onde o SVM ainda serve hoje

Três usos rasos, todos no lab ou ao lado dele:

1. **Baseline sobre embeddings.** Mean-pool (ou TF-IDF) + `SVC(kernel="linear")` vs. logística. Se o linear já separa “sinistro” de “código”, o LLM não ganha essa classificação. Guardrail: não gaste decoder onde um hiperplano basta.
2. **Classificador leve.** Poucos mil exemplos, CPU, sem GPU. Soft-margin com C escolhido em validação. Vetores de suporte = exemplos que realmente empurram a fronteira — úteis para auditoria.
3. **Guardrail raso.** Antes do SFT/JSON: um SVM no embedding da *query* (“é sinistro de auto?”). Recusa fora de domínio barato. Não é alinhamento, não é DPO, não é o A8. É um portão.

O A13.3 compara linear, RBF e logreg nas mesmas frases. RBF que ganha no treino e empata no eval não é vitória: é capacidade extra sem certificado.

---

## 10. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| 3 pontos, 8 dicotomias | **8/8**, `estilhaça=true` |
| 4 pontos / XOR | 14/16 separáveis; XOR **não** (`linearmente_separavel=false`) |
| C = 0,01 → 100 | n_sv **68 → 58**; margem **6,60 → 4,99** (blobs que se tocam, acc ~0,67) |
| encoder | **smollm2-135m-meanpool** (576-d); TF-IDF 229-d também no JSON |
| TF-IDF linear / RBF / logreg | treino **1,00** / eval **1,00** (léxico já separa) |
| embed linear / RBF / logreg | **1,00 / 1,00**; RBF **0,938 / 1,00**; logreg **1,00 / 1,00** |
| rótulos aleatórios (TF-IDF) | SVM RBF treino **1,00** eval **0,50**; MLP treino **1,00** eval **0,67** |
| ponte A5 | acc **1,00 / 0,50**; `termo_lora=inf` (`vacuo=true`); h=3, n=4: ε=**1,55** (também vácuo) |

---

## 11. O que fazer agora

1. `python modulo-a13/lab/lab_a13.py` (sem embed: `TRILHA_A13_EMBED=0`).
2. CA13 com o JSON **seu**, ligando A5 1,00/0,50 à pergunta de 1971.
3. Não escreva “VC explica o LLM”. O gabarito zera isso.
