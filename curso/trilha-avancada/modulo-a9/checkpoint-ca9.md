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
| Split | `a9_3.split` | n_eval ≥ 50, n_treino ≥ 16, `prompts_disjuntos` |
| Seeds | `a9_3.seeds`, `corridas` | **≥ 3** seeds |
| Antes (base) | `eval_antes` | n, `recompensa_media`, `n_acertos` |
| Depois | `resumo.eval_depois`, `resumo.delta` | **média e desvio** |
| Melhora | `resumo.melhorou_claro` | true **ou** parágrafo honesto se false |
| Zero-std | `resumo.frac_passos_zero_std` | reportar; não precisa ser 0 |
| `beta` default | `a9_3.beta` | **0.0** nesta receita |
| Testes `modelo` | `pytest -q` marca `modelo` | passam |

Um único flip em n=4 **não** basta. Copiar 0,600→0,733 da autoria sem rodar zera. Copiar o demo do M09 (sem `train()`) zera `atualiza_pesos`.

## CA9.4 — beta > 0 e hack no gerado

| Critério | Campo | Limiar |
| --- | --- | --- |
| KL de fato | `a9_4.beta_pos.kl_n_nao_zero` | **≥ 1** (ou `falhou`/`pulado_env` documentado) |
| Mesmo protocolo | `max_steps`, `num_generations` | iguais ao A9.3 |
| Hack vs exata no base | `hack_vs_exata_no_base` | os dois números |

## CA9.5 — T4 (não exigido)

`nao_calibrado` se `gpu` é null.

## Rubrica (0–10)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON próprio; 3 seeds; n_eval≥50; média±desvio; KL não nulo ou falha documentada; parágrafo honesto sobre zero-std / T4 |
| 7–8 | Limiares ok; trata n=3 como IC 95% |
| 5–6 | JSON de outro / n_eval=4 de versão antiga |
| 0–4 | Sem JSON; “o M09 já era GRPO”; IC inventado |

Se `melhorou_claro=false`, o relatório que cita média e desvio vale nota cheia nesse item. Inventar subida zera.
