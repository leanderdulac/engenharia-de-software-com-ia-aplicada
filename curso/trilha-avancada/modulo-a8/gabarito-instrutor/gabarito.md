# Gabarito A8 (instrutor)

Preenchido com a corrida real da VM de autoria **depois** do split treino/eval e da correção de fronteira BPE. Se o aluno rodar outro `trl` / outros passos, **os limiares do checkpoint mandam**, não estes números literais.

Os dois pares de caderno (`logp_w = −2,0 / −1,5`, …) são pedagogia, não item secreto de CA8.

## Ambiente da autoria

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md). CPU, sem CUDA, torch 2.15.0+cpu, transformers 5.22.2, trl 1.17.1, peft 0.21.2, datasets 5.2.0, corrida 2026-11-12T14:08:39Z, `segundos_total=23.857`.

| Item | Medido na autoria | Limiar do aluno |
| --- | --- | --- |
| Split | treino **10**, eval **4**, `prompts_disjuntos=true` | n_treino≥8, n_eval≥3, disjuntos |
| Fronteira tokenizer | **ok**, 0 falhas | `fronteira_tokenizer.ok=true` |
| Aviso TRL `'":'` / prefixo | **`ocorreu=false`**, 0 no stderr | `aviso_prefixo_trl.ocorreu=false` |
| A8.1 chars chosen / rejected | **60,21 / 74,29** (razão **1,23**) | `rejeitado_mais_longo=true` |
| A8.1 exemplo DPO / IPO / … | 0,6467 / 17,056 / 1,041 / 0,351 / 0,488 | finitos > 0 |
| A8.2 `train_loss` DPO 8 passos | **0,679734** | finito |
| TRL `eval_rewards/accuracies` (hold-out) | **1,0** (n=4) | reportado; n pequeno |
| TRL `eval_rewards/margins` | **0,068527** | finito |
| `avaliacao_treino_depois.rewards_accuracies` | **1,0** (n=10) | overfit esperado |
| `avaliacao_eval_depois.rewards_accuracies` | **1,0** (n=4) | o campo do CA; **não** exigir >0,5 se o aluno medir outro |
| margem log-ratio treino / eval | **1,110 / 0,661** | eval < treino nesta VM |
| `preferencia_bruta` eval | **0,500 → 0,500** | não precisa subir |
| A8.3 mesmo lote DPO/IPO/SimPO/ORPO/KTO | 0,661 / **19,063** / 0,414 / 1,576 / 0,492 | `nao_e_ranking=true` |
| `dpo_vs_beta` 0,1 / 0,5 / 1,0 | 0,661 / 0,549 / 0,442 | mesmos logps |
| IPO / KTO / ORPO / SimPO fumaça | 25,0 / 0,499 / 2,917 / 2,297 | `experimental` em ORPO/SimPO |
| A8.5 T4 | `nao_calibrado` | obrigatório nesta CPU |

Acurácia 1,0 no eval é **4/4**. Não há IC. Margem implícita no eval (0,66) é menor que no treino (1,11): o hold-out *existe*, mesmo quando a fração binária satura. `preferencia_bruta` 0,5 continua. Parágrafo que só copia 1,0 sem n=4 / margem / treino vs eval fica no teto 8.

A autoria **anterior** (treino=eval, n=12, aviso `'":'`, acc 0,917) **não** vale mais. Aluno que colar 0,917 zera honestidade.

IPO 19 vs DPO 0,66: unidades. `nao_e_ranking` tem de ser true.

## Como conferir um `ca8.json` entregue

1. `a8_1.split.prompts_disjuntos` e `fronteira_tokenizer.ok`.
2. `aviso_prefixo_trl.ocorreu=false`. Se true, o aluno não fechou o prompt no limite de token.
3. Accuracies cobradas = `avaliacao_eval_depois` / `eval.eval_rewards/accuracies`, **não** o log de treino.
4. `honestidade.sft_trilha` declara base. `a8_5_t4=nao_calibrado` se `gpu` é null.
5. Parágrafo cita eval **e** a tabela sem ranking.

## Erros comuns

| Sintoma | Causa típica | Não faça |
| --- | --- | --- |
| aviso `'":'` | prompt termina no meio do JSON | peça newline + JSON inteiro na compleção |
| acc 1,0 no treino vendida como eval | `eval_dataset=train` | cobre `n_eval` e prompts disjuntos |
| IPO “pior” | unidades | `nao_e_ranking` |
| 0,917 colado | JSON da versão sem hold-out | `epoch_unix` / `n_eval` |

```bash
cd curso/trilha-avancada
python -m pytest modulo-a8/testes -q
```

Caderno (iguais à aula): `Δ par0 = 1.9`, `L_DPO par0 ≈ 0.60265`, exemplo_aula dpo=0.64665 ipo=17.056.
