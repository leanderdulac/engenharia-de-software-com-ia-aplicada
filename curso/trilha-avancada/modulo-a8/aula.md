# A8 — Alinhamento por preferências

Trilha avançada, **opcional**. Guia da pasta: [`README.md`](./README.md). Checkpoint: [`checkpoint-ca8.md`](./checkpoint-ca8.md). Esta aula **não** contém gabarito de CA8.

No M09 você viu um JSONL de pares Amplitude e um cheatsheet de DPO **sem treinar**. No A2 abriu o bloco que produz logits. Aqui a conta de *preferência* abre: o que é um par `chosen`/`rejected`, por que RLHF treina um reward model, como o DPO elimina o laço de RL, e o que muda na família (IPO, SimPO, ORPO, KTO). Ao final você deve conseguir, no papel e no código:

1. escrever um par `prompt` / `chosen` / `rejected` e dizer o que o rótulo *não* mede;
2. contrastar SFT (só o texto bom) com otimização por preferência (contraste);
3. derivar a perda DPO a partir de RLHF + Bradley-Terry, sem decorar a fórmula;
4. dizer o que `beta` faz, e por que comprimento do `rejected` vira viés;
5. situar IPO, SimPO, ORPO e KTO — e marcar o que, no TRL desta VM, é API estável vs `trl.experimental`.

Nada disto entra nas 240 h. Não substitui C09.*. Os dois pares numéricos da §5 foram conferidos em [`lab/perdas.py`](./lab/perdas.py) (`exemplo_numerico_aula`). Rewards, accuracies e margem **não** se copiam da aula: saem do seu `ca8.json`.

---

## 0. Honestidade de dependências

A ordem de *construção* entregou A8 antes do A5. **A5 agora existe:** DPO parte de **π_SFT** quando `modulo-a5/execucao/pi_sft/` está no disco (`TRILHA_PI_SFT=0` volta ao base). A6 ainda é esqueleto. Consequências:

| O plano original pedia | O que este módulo faz |
| --- | --- |
| SFT da trilha (A5) como `π_ref` / `π_SFT` | `carregar_base_ou_sft()`: merge do LoRA A5 se houver adapter; senão SmolLM2-135M **base** + LoRA `q_proj`/`v_proj` |
| Pares do harness Amplitude / JSONL do M09 | pares **originais** no *padrão* do M09 (JSON vs prosa, vírgula decimal → `125000`) com nomes já usados no A2 (`Ana Souza` / `ABC-1D23`), **split treino/eval**. O arquivo `preference-dataset-amplitude.jsonl` **não** é lido nem republicado |
| DPO LoRA na T4, `rewards/accuracies` > 0,5 com IC, harness sem queda > 2 p.p. | treino **CPU**, 8 passos, n=12 (overfit esperado). T4 / IC / harness = `nao_calibrado` |
| Cinco treinos completos da família | DPO sigmoid de verdade (8 passos); IPO e KTO na API **estável** (fumaça de 1–2 passos); ORPO e SimPO em `trl.experimental` (1 passo). A tabela justa é a **mesma perda no mesmo lote de logps** |

Se você abrir o JSON e `a8_5_t4.status` estiver `nao_calibrado`, isso é o desenho, não um bug seu.

---

## 1. O que um par de preferência *é*

SFT mostra um texto “certo” e pede `−log π(y | x)` token a token. Preferência mostra *dois* textos e um rótulo relativo: “neste prompt, **este** é melhor que **aquele**”. Convenção desta aula e do TRL:

```text
prompt     x      o que o usuário pediu
chosen     y_w    a compleção preferida  (w = winner)
rejected   y_l    a compleção rejeitada  (l = loser)
```

O rótulo **não** diz que `y_w` é verdade, nem que é o JSON do harness, nem que um humano da Amplitude clicou. Diz só: *neste dataset, alguém (humano, regra, ou modelo-juiz) preferiu y_w a y_l dado x*.

Três falhas típicas do caso Amplitude, reconstruídas aqui sem copiar o JSONL do tronco:

1. **Formato.** Pediu JSON com `segurado` / `placa` / `valor`; o modelo respondeu em prosa.
2. **Schema.** Devolveu `nome` / `veiculo` / `preco` em vez das chaves combinadas.
3. **Vírgula decimal.** `R$ 1250,00` vira `125000` (o harness do M09 já caçou isso).

Um par *não* precisa ser amostra do modelo atual. Pode ser regra: JSON curto vs. enrolação. Isso é honesto e barato. O preço: o modelo pode aprender o atalho errado — “seja curto” em vez de “seja JSON” (§8).

KTO (Ethayarajh et al., 2024) relaxa o par: cada linha é `(x, y, desejável?)`. O lab converte cada par DPO em duas linhas KTO (`label=True` no chosen, `False` no rejected). Não é o mesmo sinal estatístico.

---

## 2. Reward model, RLHF, RLAIF

A pipeline clássica (Ziegler et al. 2019; Ouyang et al. 2022, *InstructGPT*) tem três estágios:

1. **SFT** em demonstrações. Sai `π_SFT`.
2. **Reward model.** Humanos comparam pares gerados (ou misturados). Treina-se `r_φ(x, y)` para que `r_φ(x, y_w) > r_φ(x, y_l)`. A verossimilhança usual é Bradley-Terry (1952):

```text
P(y_w ≻ y_l | x) = σ( r(x, y_w) − r(x, y_l) )
```

`σ` é a logística. A perda do RM é `−log` dessa probabilidade — uma classificação binária na *diferença* de recompensa. O partição / o valor absoluto de `r` não aparece: só a diferença.

3. **RL.** Maximiza `r_φ` na política, com um travão para não fugir do SFT:

```text
max_π  E_{y ~ π(·|x)} [ r_φ(x, y) ]  −  β  KL( π(·|x)  ||  π_ref(·|x) )
```

`π_ref` costuma ser `π_SFT`. `β` grande = fique perto do SFT (menos “personalidade nova”, menos colapso de modo). O algoritmo típico no papel é PPO (Schulman et al. 2017). Na prática isso é um laço: amostrar da política, pontuar com o RM, atualizar, o RM fica *fora da distribuição*, às vezes se retreina.

**RLAIF** troca o rótulo humano por um modelo-juiz (Bai et al. 2022, *Constitutional AI*; Lee et al. 2023). A matemática do RM/RL não muda. O que muda é *quem* prefere, o viés do juiz, e o custo. Esta aula não treina juiz.

Nesta trilha **não há SFT do A5**. O `π_ref` do lab é o SmolLM2-135M congelado. Isso é mais frágil do que o paper: o base não foi ensinado a emitir o JSON da Amplitude. DPO ainda *pode* aumentar a margem implícita entre `y_w` e `y_l` — e é isso que o lab mede. Não confundir com “o modelo agora passa no harness”.

---

## 3. DPO: o modelo *é* o reward (derivação intuitiva)

Rafailov et al. 2023 partem da mesma equação (3) do RLHF. Sob o KL, a política ótima para um reward `r` tem forma fechada:

```text
π_r(y|x)  ∝  π_ref(y|x)  ·  exp( r(x,y) / β )
```

Há uma constante de normalização `Z(x)` (soma/integral em *todas* as y). Isolando `r`:

```text
r(x,y)  =  β log( π_r(y|x) / π_ref(y|x) )  +  β log Z(x)
```

Bradley-Terry só vê **diferença** `r_w − r_l`. O `Z(x)` é o mesmo nos dois lados e **cancela**. Sobram só as políticas:

```text
P(y_w ≻ y_l | x)  =  σ(  β · (  log π(y_w|x)/π_ref(y_w|x)
                               − log π(y_l|x)/π_ref(y_l|x) ) )
```

Chame `Δπ = log π(y_w|x) − log π(y_l|x)` (soma dos log-probs da *compleção*, não da média — o TRL e este lab usam soma). `Δref` é a mesma conta no modelo de referência. A perda DPO é a NLL dessa logística:

```text
L_DPO  =  − log σ( β (Δπ − Δref) )
```

Intuição operacional, caso Amplitude:

- Se a política aumenta a log-prob do JSON (`y_w`) *relativa* à prosa (`y_l`) **mais** do que o base já fazia, `Δπ − Δref` cresce, `σ` chega perto de 1, a perda cai.
- Se ela só infla os dois textos por igual, a diferença não mexe.
- Se ela foge demais do base, o termo `− Δref` (na prática, o ratio contra `π_ref`) puxa de volta — é o KL do RLHF, sem amostrar PPO.

O “reward implícito” do DPO é exatamente `r̂(x,y) = β log(π_θ(y|x) / π_ref(y|x))`. O TRL loga isso como `rewards/chosen`, `rewards/rejected`, `rewards/margins` (= diferença) e `rewards/accuracies` (= fração de pares com margem > 0).

**Não** avalie a política *contra ela mesma* como referência: a margem vira zero por construção. O lab congela o SmolLM2 base e usa esse base como `π_ref` na conta de logps.

---

## 4. `beta`, IPO, SimPO, ORPO, KTO

### `beta`

No objetivo RLHF, **`β` grande** = penalidade KL maior = política ótima mais perto de `π_ref`. No DPO, o mesmo `β` escala o argumento da `σ`. Com `β` pequeno você precisa de um `Δπ − Δref` *maior* para a mesma confiança — a política pode se afastar mais. Valores típicos nos papers: 0,1 a 0,5. O lab treina com `β = 0,1` e, *sem retreinar*, recoloca os mesmos logps na fórmula com `β ∈ {0,1, 0,5, 1,0}`. Isso **não** é um sweep de treino: é a mesma política, perda diferente. Não leia “β maior → loss menor” como “β maior treina melhor”.

### IPO (Azar et al. 2023)

O paper argumenta que substituir preferências por um reward pontual (Bradley-Terry) é uma aproximação, e que o DPO ainda herda isso. A família ΨPO usa a preferência *pareada*. O caso Identidade (IPO) vira um quadrado:

```text
L_IPO  =  ( h − 1/(2β) )²     com  h = Δπ − Δref
```

O alvo não é “margem infinita” (sigmoid saturada): é uma margem **finita** `1/(2β)`. Com `β = 0,1`, o alvo é `h = 5` em espaço de *soma* de log-probs. Isso é enorme para compleções curtas. No lote depois do DPO desta VM, a IPO no mesmo `h` ficou ~19, enquanto a DPO sigmoid já estava ~0,66 — a sigmoid saturada, o quadrado ainda longe do 5. Lição: **não compare o valor cru das perdas entre métodos**. Unidades diferentes.

API estável: `trl.DPOTrainer(loss_type="ipo")`.

### SimPO (Meng, Xia, Chen 2024)

Sem modelo de referência. A recompensa implícita é a **média** de log-prob por token, com uma margem `γ`:

```text
L_SimPO  =  − log σ( β (logp̄_w − logp̄_l) − γ )
```

Normalizar por `|y|` ataca o viés de comprimento (§8). O preço: sem `π_ref`, não há o travão KL explícito do DPO. No TRL 1.17.1 desta VM, SimPO vive em **`trl.experimental.cpo.CPOTrainer` com `loss_type="simpo"`** — não está na API estável.

### ORPO (Hong, Lee, Thorne 2024)

Sem referência também. Soma SFT no chosen com um termo de *odds ratio* que empurra o rejected para baixo, no mesmo passo:

```text
L_ORPO  ≈  L_SFT(y_w)  +  λ · (− log σ( logp_w − logp_l ))
```

A fórmula da aula é um *esquema* (odds no espaço de log-prob da compleção, não o odds token a token do paper). Serve para a tabela no mesmo lote. Treino de verdade: **`trl.experimental.orpo.ORPOTrainer`**.

### KTO (Ethayarajh et al. 2024)

Não precisa de par. Cada compleção é desejável ou não; a perda parece uma utilidade Kahneman-Tversky em `Δ = log π(y|x) − log π_ref(y|x)`. O lab implementa um esquema (`1−σ` no chosen, `σ` no rejected). O `KTOTrainer` do TRL é mais rico (baseline de KL no lote). API **estável**: `trl.KTOTrainer`.

### Tabela da família (TRL 1.17.1, conferido nesta VM)

| Método | Precisa `π_ref`? | Par? | O que otimiza (aula) | API nesta VM |
| --- | --- | --- | --- | --- |
| DPO sigmoid | sim | sim | `−log σ(β (Δπ−Δref))` | `trl.DPOTrainer` **estável** |
| IPO | sim | sim | `(h − 1/(2β))²` | `trl.DPOTrainer(loss_type="ipo")` **estável** |
| KTO | sim | não | utilidade em Δ vs ref | `trl.KTOTrainer` **estável** |
| ORPO | não | sim | SFT + odds-ratio | `trl.experimental.orpo` |
| SimPO | não | sim | média por token + γ | `trl.experimental.cpo` `loss_type=simpo` |

A tabela *numérica* do lab (A8.3) aplica as cinco fórmulas aos **mesmos** logps do hold-out. Isso **não é ranking de qualidade**. Unidades:

| Coluna | Unidade |
| --- | --- |
| DPO / SimPO | `−log σ(·)` ∈ (0, ∞), satura perto de 0 |
| IPO | quadrado `(h − 1/(2β))²` — com β=0,1 o alvo é h=5; dezenas são o normal |
| ORPO (esquema) | SFT (`−logp/n`) + λ · odds |
| KTO (esquema) | utilidade em [0, 1] aprox. |

Um IPO 19 ao lado de um DPO 0,66 **não** diz que o IPO “treinou pior”. O JSON traz `nao_e_ranking: true`. A8.4 só acende os trainers (fumaça): `train_loss` de 1 passo ORPO contra 8 passos DPO também não compete.

---

## 5. Conta à mão (dois pares, não é o lab)

Números de [`perdas.exemplo_numerico_aula`](./lab/perdas.py). Soma de log-prob:

```text
par 0:  logp_w = −2.0   logp_l = −4.0   logp_w_ref = −2.2   logp_l_ref = −2.3
par 1:  logp_w = −1.5   logp_l = −1.6   logp_w_ref = −1.5   logp_l_ref = −1.55
β = 0,1
```

Par 0:

```text
Δπ   = −2.0 − (−4.0) = 2.0
Δref = −2.2 − (−2.3) = 0.1
h    = 2.0 − 0.1     = 1.9
β h  = 0.19
σ(0.19) = 1 / (1 + e^{−0.19}) ≈ 0.5474
L_DPO_0 = −log 0.5474 ≈ 0.6027
```

Par 1: `h = 0,05`, quase empate — a sigmoid mal saiu de 0,5. Média dos dois: DPO ≈ **0,6467**. IPO: alvo `1/(2β) = 5`; média de `(1,9−5)²` e `(0,05−5)²` ≈ **17,06**. SimPO (média por token, `β=2`, `γ=0,5`) ≈ **1,041**. ORPO esquema ≈ **0,351**. KTO esquema ≈ **0,488**.

Confira com `python -c "from perdas import exemplo_numerico_aula; print(exemplo_numerico_aula())"` a partir de `modulo-a8/lab/`. Se o seu número do *lab* (SmolLM2) não bater com 0,6467, está certo: aquele é o exemplo de caderno.

---

## 6. SFT versus otimização por preferência

| | SFT | DPO (e família com par) |
| --- | --- | --- |
| Dado | `(x, y*)` | `(x, y_w, y_l)` |
| Gradiente | sobe `y*` | sobe `y_w` *relativo* a `y_l` (e a `π_ref`, no DPO) |
| O que pode falhar | clonar demonstrações ruins; não sabe o que *evitar* | aumentar a margem diminuindo os dois; aprender “seja curto”; overfit em n pequeno |
| Quando basta | formato já está no SFT, sem contraste claro | o modelo já *sabe* os dois estilos e você quer empurrar um |

SFT **não** é um DPO com `y_l` vazio. Sem o rejected, não há Bradley-Terry. ORPO é o híbrido explícito (SFT + contraste no mesmo passo). Com o A5 publicado, o lab *tenta* o paper (“DPO em cima de SFT”) via `honestidade.ponto_partida`. Os testes isolados (`TRILHA_PI_SFT=0`) ainda medem LoRA no base.

---

## 7. O que o lab mede (e o que não)

**A8.1.** Pares de **treino** e de **avaliação** com prompts disjuntos; comprimento em caracteres. Compleções rejected em prosa continuam mais longas (viés, §8). O campo `fronteira_tokenizer.ok` tem de ser true: `tokenize(prompt)` é prefixo de `tokenize(prompt+compleção)` nos dois lados. A correção é formatação — um `\\n` no fim do prompt, e **não** cortar JSON no meio de `":` (BPE funde `'":'` com o que vem depois).

**A8.2.** `DPOTrainer` estável, LoRA r=8 em `q_proj`/`v_proj`, `max_steps=8`, `max_length=128`, `β=0,1`, CPU. O `eval_dataset` do TRL é o hold-out. `eval_rewards/accuracies` **não** é medido no conjunto de treino. O JSON também traz `avaliacao_treino_*` (overfit) e `avaliacao_eval_*` (o que o CA8 cobra). `aviso_prefixo_trl.ocorreu` tem de ser false.

Dois números que *não* são a mesma coisa:

- `preferencia_bruta` = fração com `logp(y_w) > logp(y_l)` (soma crua, sem ref).
- `rewards_accuracies` = fração com margem *implícita* vs o base congelado.

Lição: acurácia alta **no treino** (versão anterior desta aula chegou a 0,92 em 12 pares vistos) não é win-rate nem harness. O número que vale no checkpoint é o do **eval**. Copiar 0,917 da autoria antiga zera. O CA8.5 (T4 + IC + harness) continua `nao_calibrado`.

Se o aviso de prefixo voltar no seu log, o JSON `fronteira_tokenizer.falhas` mostra o recorte — não invente que “sumiu”.

**A8.3.** Cinco perdas no mesmo lote + `dpo_vs_beta` {0,1, 0,5, 1,0} nos logps congelados.

**A8.4.** KTO 2 passos (estável), IPO 1 passo (estável, fumaça), ORPO e SimPO 1 passo (`experimental`). `train_loss` desses smoke tests **não** entra na comparação justa.

**A8.5.** Campo explícito `nao_calibrado`. Colab T4: o README diz como *rodar*; não há número desta VM para colar.

---

## 8. Viés de comprimento

DPO soma log-probs. Uma prosa de 40 tokens, mesmo razoável por token, acumula soma mais negativa que um JSON de 12 tokens. O otimizador pode aprender “ganhe diminuindo `|y_l|`” ou, simetricamente, “ganhe encurtando `y_w`”. SimPO média por token justamente para isso. IPO com alvo `1/(2β)` em *soma* herda o mesmo viés, só que com unidade diferente.

Antes de treinar, o lab imprime `estatistica_comprimento`. Se `rejeitado_mais_longo=true` (aqui é), o parágrafo do CA8.1 tem de dizer o que isso *pode* ensinar, não só a média. Corrigir o dataset para empatar comprimentos é válido — desde que você meça de novo e não invente que o DPO “não tem viés”.

---

## 9. Avaliação, além do `train_loss`

| Sinal | O que é | O que não é |
| --- | --- | --- |
| `train_loss` DPO | NLL da sigmoid no batch | qualidade gerada |
| `rewards/accuracies` | pares com `r̂_w > r̂_l` vs ref | win-rate com juiz, nem JSON válido |
| `rewards/margins` | média de `r̂_w − r̂_l` | pontos do harness |
| `preferencia_bruta` | soma logp sem ref | a métrica do paper |
| comprimento | chars/tokens de y_w vs y_l | estilo |
| harness Amplitude / IC | formato, vírgula decimal, bootstrap | **não calibrado** neste módulo |
| juiz (RM ou LLM) | preferência amostrada | o lab não treina juiz |

Regra da trilha: número que não saiu do seu JSON ou de `exemplo_numerico_aula` não entra no parágrafo.

---

## 10. O que fazer agora

1. Ler esta aula até §5 e conferir os dois pares no caderno.
2. `python modulo-a8/lab/lab_a8.py` a partir de `curso/trilha-avancada/` (CPU; ~meia minuto nesta VM com pesos em cache).
3. Abrir `modulo-a8/saidas/ca8.json` e preencher CA8 com *os seus* campos.
4. Opcional: tutor com [`tutor/mapa-a8.md`](./tutor/mapa-a8.md). Não vale nota.

T4/Colab: instale `trl peft datasets transformers` **sem** trocar o `torch` CUDA pelo wheel CPU. Marque o JSON como T4 se `ambiente.gpu` existir. Não copie accuracies de outra máquina — use o `avaliacao_eval_depois` do *seu* JSON.
