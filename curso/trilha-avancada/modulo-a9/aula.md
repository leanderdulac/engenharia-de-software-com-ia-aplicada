# A9 — RL com recompensa verificável

Trilha avançada, **opcional**. Guia da pasta: [`README.md`](./README.md). Checkpoint: [`checkpoint-ca9.md`](./checkpoint-ca9.md). Esta aula **não** contém gabarito de CA9.

No A8 você alinhou por *preferência* (DPO: par chosen/rejected, sem amostrar a política no laço). No M09 o script `grpo_verifiable_reward_demo.py` calcula vantagem de grupo **sem atualizar pesos**. Aqui o laço fecha: política, ação, recompensa, trajetória; REINFORCE; PPO; GRPO que **treina**. Ao final você deve conseguir:

1. nomear estado/ação/recompensa/trajetória num LLM (prompt → tokens → r no fim);
2. dizer se o algoritmo é on-policy e o que isso custa;
3. escrever o gradiente REINFORCE e o papel do baseline;
4. situar clipping e vantagem no PPO, e a vantagem *relativa ao grupo* no GRPO;
5. contrastar recompensa verificável (formato, conta) com RM aprendido, e reconhecer reward hacking;
6. comparar SFT × DPO × PPO × GRPO sem fingir que treinou os quatro nesta CPU.

Nada disto entra nas 240 h. Não substitui C09.*. A curva do bandit sai de [`lab/reinforce.py`](./lab/reinforce.py). Recompensa do SmolLM2 **não** se copia da aula: sai do seu `ca9.json`.

---

## 0. Honestidade de dependências

**A7 (raciocínio treinável) ainda é esqueleto.** A5/A6 também. Consequências:

| O plano original pedia | O que este módulo faz |
| --- | --- |
| SFT da trilha como política inicial | GRPO no **SmolLM2-135M base** + LoRA `q_proj`/`v_proj` |
| Demo GRPO do M09 | **não copiado**; aquele script não dá `optimizer.step` |
| Tarefa Amplitude / harness | soma curta (`3+4` → primeiro inteiro `7`) |
| GRPO na T4, G grande, IC no retido | CPU, G=4, 16 passos, **3 seeds**, n_eval=80; T4 = `nao_calibrado` |

O prompt **termina em `=`**, sem newline extra. Um `\n` depois do igual faz o base emitir `A. 10` e a recompensa some. A recompensa de precisão **não** exige que a compleção inteira seja o dígito (6 tokens do base continuam, `4\n\nA = `): o sinal é o **primeiro inteiro** parseado.

---

## 1. Política, ação, recompensa, trajetória

Num LLM:

| Peça de RL | Aqui |
| --- | --- |
| Estado `s` | o prefixo já gerado (prompt + tokens até agora) |
| Ação `a` | o próximo token |
| Política `π_θ(a\|s)` | softmax dos logits |
| Trajetória `τ` | a compleção inteira |
| Recompensa `r` | em geral **no fim** (a soma está certa? o texto é um inteiro?) |

Credit assignment: o sinal chega tarde. GRPO (e o DPO) espalham um escalar da *sequência* por todos os tokens da compleção — não há crítico token a token neste lab.

**On-policy:** as amostras que entram no gradiente vêm da política *atual* (PPO, GRPO, REINFORCE). Caro: cada passo gera de novo. **Off-policy:** reusa pares velhos (DPO no JSONL). Mais estável de engenharia, viesado se a política já saiu daquele suporte.

---

## 2. REINFORCE

Williams (1992). Uma ação `a`, retorno `G` (aqui: r ∈ {0,1}):

```text
∇_θ J  ≈  (G − b)  ∇_θ log π_θ(a)
```

`b` (baseline) não muda o valor esperado do gradiente se não depender de `a`; reduz variância. No lab, `b` é uma média móvel da recompensa.

Bandit de 4 ações, só a ação 1 paga 1. Nesta VM, 200 passos, semente 0: com baseline a recompensa média 0,40 → **1,00**, `p(ótima)=0,972`; sem baseline também chega (`p=0,982`). Neste brinquedo o baseline não é necessário para *aprender* — a lição é a fórmula, não “baseline sempre ganha em 200 passos”.

---

## 3. PPO: clipping e vantagem

PPO (Schulman et al. 2017, [1707.06347](https://arxiv.org/abs/1707.06347)) é on-policy com um travão. Razão de importância `ρ = π_θ(a|s) / π_θold(a|s)`. A perda clipada (esquema):

```text
L = − min( ρ Â,  clip(ρ, 1−ε, 1+ε) Â )
```

`Â` é vantagem (retorno minus baseline/crítico; GAE no paper, [1506.02438](https://arxiv.org/abs/1506.02438)). `ε≈0,2`: se a política nova discordar demais da que gerou o lote, o clip mata o gradiente. Custa um **crítico** (valor) extra — memória, instabilidade.

GRPO joga o crítico fora.

---

## 4. GRPO: vantagem relativa ao grupo

DeepSeekMath (Shao et al. 2024, [2402.03300](https://arxiv.org/abs/2402.03300)). Para um prompt `x`, amostra **G** compleções da política atual. Recompensa verificável `r_i` em cada uma. Vantagem:

```text
Â_i  =  ( r_i − mean(r) ) / ( std(r) + ε )
```

Sem rede de valor. O sinal é: *melhor que as irmãs deste prompt*. Se **todas** tomam o mesmo `r`, o desvio é zero — `frac_reward_zero_std=1` no TRL — e o gradiente some. Nesta CPU isso aconteceu no **3º** passo (`reward=0`, `grad_norm=0`); nos dois primeiros o grupo teve `std≈0,71` e `grad_norm` 0,67 e 1,10.

A perda parece PPO (razão × vantagem, clip), com KL opcional:

```text
L  +=  β  KL(π_θ  ||  π_ref)
```

No TRL 1.17.1 o **beta padrão é 0.0**: não carrega ref, mais barato. DeepSeek-R1 ([2501.12948](https://arxiv.org/abs/2501.12948)) cita `β≈0,001` e recompensas de precisão/formato. O lab treina de verdade com `β=0` (16 passos, G=4, 3 seeds) e compara `β=0,04` no mesmo G/passos/seed=0 — o log traz `kl` **não nulo** depois do 1º passo.

`num_generations ≥ 2` (senão não há grupo). Nesta CPU `G=4`, `temperature=1,0`, `max_completion_length=8`. Mesmo assim ~1/5 dos passos ainda sai com `frac_reward_zero_std=1` (grupo homogêneo). Currículo curto + G maior *reduz*, não zera.

---

## 5. Recompensa verificável vs RM

| | Verificável | Reward model (A8) |
| --- | --- | --- |
| Sinal | regra: primeiro inteiro == ouro; JSON parseia; teste passa | rede treinada em pares |
| Barato depois de escrita | sim | rótulo humano/AI |
| Hacking | otimiza a *regra*, não a intenção | otimiza o RM, inclusive falhas dele |

Três regras neste lab, ouro `7`:

- `recompensa_exata`: 1 se o **primeiro inteiro** da compleção é `7`.
- `recompensa_formato`: 1 se a compleção *inteira* (strip) é só um inteiro.
- `recompensa_hack_digito`: 1 se existe **qualquer** dígito (`"0"` e `"70"` ganham).

Caderno: exata `[1,0,0,0,0]`, formato `[1,1,1,0,0]`, hack `[1,1,1,0,0]`, 2 divergências hack vs exata (`"0"`, `"70"`). `"7 pontos"` passaria na exata (primeiro inteiro 7) e falharia no formato estrito.

No SmolLM2 base, greedy 8 tokens nos 20 primeiros do hold-out: exata **0,35**; hack **1,00**. Treinar no hack empurra “solte um número”, não “acerta a soma”.

---

## 6. O que o lab mediu

Hold-out **n=80**, prompts disjuntos do treino (24 contas de currículo). Eval greedy do **base** (não depende da seed): **0,600** (48/80). Treino greedy do base: 0,708 (17/24).

Três seeds independentes, `β=0`, G=4, 16 passos, ~69 s no total desta VM:

| seed | eval depois | delta | passos com std=0 |
| ---: | ---: | ---: | ---: |
| 0 | 0,738 (59/80) | +0,138 | 5/16 |
| 1 | 0,725 (58/80) | +0,125 | 4/16 |
| 2 | 0,738 (59/80) | +0,138 | 1/16 |
| **média ± desvio** | **0,733 ± 0,007** | **+0,133 ± 0,007** | 0,21 ± 0,13 |

`melhorou_claro=true`: a média do delta é positiva, ≥ 0,03 e maior que o desvio entre seeds. n=3 **não** é IC 95%; o desvio entre seeds é pequeno (~1 exemplo em 80). Um único flip em n=4 (versão anterior desta aula) *era* ruído; este não.

Treino depois: 21/24 (0,875) nas três seeds — também sobe, mas o que conta no CA9 é o **eval**.

Passos com `frac_reward_zero_std=1` **não desapareceram**. G=4 e currículo curto baixam a fração (~1/5); um grupo todo certo ou todo errado ainda zera o Â. Completions em 8 tokens, muitas clipadas.

`β=0,04`, mesmos 16 passos, seed=0: `kl` no log em **15/16** passos (`kl_max≈0,016`). Eval **0,738** — igual ao `β=0` seed 0 nesta CPU. O KL *aparece*; não há ganho extra de qualidade para declarar. DeepSeek-R1 usa `β≈0,001`; 0,04 é só para o termo ser visível no log.

---

## 7. SFT × DPO × PPO × GRPO

| | Dado | Amostra no laço? | Sinal | Travão |
| --- | --- | --- | --- | --- |
| SFT | `(x, y*)` | não | `−log π(y*)` | implicitamente o dado |
| DPO (A8) | `(x, y_w, y_l)` | não | sigmoid da margem vs ref | `β` no log-ratio |
| PPO | prompt; gera y | sim | RM ou regra; crítico | clip + KL |
| GRPO | prompt; G amostras | sim | regra (aqui); vantagem do grupo | clip; `β` KL (0 no TRL default) |

Nesta trilha **não** há tabela numérica SFT×DPO×PPO×GRPO no mesmo modelo: A5 ausente, PPO com crítico não cabe nesta CPU, DPO foi preferência JSON, GRPO foi soma. Um ADR de aluno que invente win-rate cruzado zera. O que cabe: esta tabela + os dois JSONs (A8 e A9) como evidência *separada*.

---

## 8. O que fazer agora

1. Conta REINFORCE no caderno (4 ações).
2. `python modulo-a9/lab/lab_a9.py` a partir de `curso/trilha-avancada/`.
3. CA9 com o `ca9.json` **seu**. n=80, 3 seeds: cite média e desvio do delta. Não invente IC.
4. Opcional: [`tutor/mapa-a9.md`](./tutor/mapa-a9.md).

T4/Colab: não troque o `torch` CUDA. Não copie 0,600→0,733 desta CPU como teto — meça.
