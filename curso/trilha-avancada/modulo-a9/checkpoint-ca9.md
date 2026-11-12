# CA9 — checkpoint objetivo (aluno)

Prática **opcional** da trilha. Não substitui C01–C09.

Entregue:

1. `saidas/ca9.json` gerado por `python modulo-a9/lab/lab_a9.py` **na sua máquina**.
2. Um parágrafo (máx. 1 página) apontando campos do JSON.

O gabarito do instrutor **não** faz parte desta entrega.

CA9.5 (T4 / G grande / IC) **não é exigido**. `a9_5_t4.status = nao_calibrado` (ou JSON T4 *seu* com `ambiente.gpu`).

## CA9.1 — REINFORCE

| Critério | Campo | Limiar |
| --- | --- | --- |
| Com e sem baseline | `a9_1.com_baseline`, `sem_baseline` | `p_otima`, médias início/fim |
| Aprendeu | `com_baseline.subiu` **ou** `p_otima > 0,25` | true / > 1/n_acoes |
| Testes | `pytest modulo-a9/testes -q -m "not modelo"` | passam |

## CA9.2 — hacking

| Critério | Campo | Limiar |
| --- | --- | --- |
| Divergência | `a9_2.n_divergencias` | **≥ 1** |
| `"0"` / `"70"` | parágrafo | hack=1, exata=0 (ou o que o JSON mostrou) |

## CA9.3 — GRPO que atualiza pesos

| Critério | Campo | Limiar |
| --- | --- | --- |
| API | `a9_3.api`, `atualiza_pesos` | `GRPOTrainer`, **true** |
| Split | `a9_3.split` | n_eval ≥ 3, `prompts_disjuntos` |
| Antes/depois no **eval** | `eval_antes`, `eval_depois` | `recompensa_media`, `n_acertos` |
| Se não subiu | `por_que_nao_subiu` | preenchido; parágrafo cita amostra |
| Se subiu | parágrafo | n do eval; **não** inventar IC; citar o flip |
| `beta` default | `a9_3.beta` | **0.0** nesta receita (TRL) |
| Testes `modelo` | `pytest -q` marca `modelo` | passam |

Inventar eval 0,99 nesta CPU zera. Copiar o demo do M09 (sem `train()`) zera `atualiza_pesos`. Copiar 0,50→0,75 da autoria sem rodar zera.

## CA9.4 — beta > 0 e hack no gerado

| Critério | Campo | Limiar |
| --- | --- | --- |
| Fumaça KL | `a9_4.beta_pos` | `ok` com `kl_log` **ou** `falhou`/`pulado_env` documentado |
| Hack vs exata no base | `hack_vs_exata_no_base` | os dois números; não precisam subir |

## CA9.5 — T4 (não exigido)

`nao_calibrado` se `gpu` é null.

## Rubrica (0–10)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON próprio; REINFORCE sobe; hacking divergente; GRPO `train()`; eval hold-out; parágrafo honesto (n pequeno / `por_que_nao_subiu` se r não mexeu); T4 declarado |
| 7–8 | Limiares ok; parágrafo trata 3/4 como IC |
| 5–6 | JSON de outro / números digitados |
| 0–4 | Sem JSON; “o M09 já era GRPO”; IC inventado |

Se a recompensa **não** subir, o relatório que explica o grupo homogêneo vale nota cheia nesse item. Inventar subida zera. n=4 com um flip também vale — desde que o parágrafo diga que é um exemplo.
