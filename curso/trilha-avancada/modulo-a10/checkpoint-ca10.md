# CA10 — checkpoint objetivo (aluno)

Prática **opcional**. Não substitui C01–C09. Gabarito do instrutor **não** entra na entrega.

Entregue `saidas/ca10.json` gerado na **sua** máquina e um parágrafo (máx. 1 página).

CA10.6 (T4 / custo/1k / IC) **não é exigido**.

## CA10.1 — professor + filtro

| Critério | Campo | Limiar |
| --- | --- | --- |
| Licença | `licencas.professor.licenca_card` | preenchida; Apache-2.0 nesta receita |
| Split | `a10_1.split` | n_eval ≥ 40, disjuntos |
| Filtro | `a10_1.filtro` | n_aceitos, taxa_aceite |
| Eval professor | `eval_professor` | acc, p50, pegada |

## CA10.2 — aluno original

| Critério | Campo | Limiar |
| --- | --- | --- |
| Eval | `a10_2.eval` | acc, p50, pegada no **mesmo** hold-out |

## CA10.3 — sequência

| Critério | Campo | Limiar |
| --- | --- | --- |
| Treino | `a10_3.passos`, `losses` | `train()` / loop com CE |
| Eval | `a10_3.eval` | acc no hold-out |

## CA10.4 — logits

| Critério | Campo | Limiar |
| --- | --- | --- |
| T | `a10_4.temperatura` | > 1 |
| KL | `a10_4.losses` | finitos |
| Máscara / shift / T² | `a10_4.diagnostico` | `shift_alinhado=true`, `mascara_inclui_prompt=false`, `t2_bate=true` |
| Eval | `a10_4.eval` | acc — **pode piorar**; o parágrafo cita o número |
| Tokenizer | `licencas.mesmo_tokenizer` | true nesta receita |

## CA10.4c — perda mista

| Critério | Campo | Limiar |
| --- | --- | --- |
| Fórmula | `a10_4c.formula` | `α·CE + (1−α)·T²·KL` |
| α | `a10_4c.alpha` | 0,5 nesta receita |
| Eval | `a10_4c.eval` | acc no mesmo hold-out; citar se subiu ou não |

## CA10.5 — tabela

Parágrafo compara professor, aluno original, sequência, logits **e** mista em qualidade, latência e memória. Sem IC inventado. Sem “logits sempre ganha”.

## CA10.6 — T4

`nao_calibrado` se `gpu` é null.

## Rubrica (0–10)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON próprio; manifesto de licença; filtro; tabela completa; parágrafo honesto se logits cair |
| 7–8 | Limiares ok; esconde a queda dos logits |
| 5–6 | JSON de outro |
| 0–4 | Sem JSON; treinou aluno com API comercial sem ler o termo |
