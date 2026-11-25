# CA8 — checkpoint objetivo (aluno)

Prática **opcional** da trilha. Não substitui C01–C09. Não vale para a média das 240 h salvo o regulamento da turma decidir depois.

Entregue um único pacote:

1. `saidas/ca8.json` gerado por `python modulo-a8/lab/lab_a8.py` **na sua máquina** (ou Colab). Não reescreva os números à mão.
2. Um parágrafo (máx. 1 página) apontando campos do JSON. Sem print sem arquivo.

O gabarito do instrutor **não** faz parte desta entrega. Se você abriu `gabarito-instrutor/`, declare.

CA8.5 **não é exigido**: T4/Colab, intervalo de confiança e harness Amplitude não foram calibrados. O JSON deve trazer `a8_5_t4.status = nao_calibrado` (ou um JSON T4 *seu*, com `ambiente.gpu` preenchido). Inventar win-rate / IC / queda de harness zera o item de honestidade.

A5 está publicado. `honestidade.ponto_partida` declara `pi_sft` ou `smollm2_base`. A6 continua esqueleto.

## CA8.1 — pares e comprimento

| Critério | Campo | Limiar |
| --- | --- | --- |
| Pelo menos 8 pares | `a8_1.n_pares` | **≥ 8** |
| Split | `a8_1.split` | `n_treino` ≥ 8, `n_eval` ≥ 3, `prompts_disjuntos=true` |
| Fronteira de token | `a8_1.fronteira_tokenizer.ok` | **true** (0 falhas); prompts terminam em newline |
| Estatística de comprimento | `a8_1.comprimento` | `chosen_chars_medio`, `rejected_chars_medio`, `razao_rejected_sobre_chosen`, `rejeitado_mais_longo` presentes |
| Lição de viés | parágrafo | diz o que rejected mais longo *pode* ensinar (não só a média) |
| Exemplo da aula | `a8_1.exemplo_aula` | `dpo_sigmoid`, `ipo`, `simpo`, `orpo`, `kto` finitos e > 0 |
| APIs marcadas | `a8_1.exemplo_aula.apis` (ou `a8_3`) | ORPO e SimPO contêm `experimental`; DPO/IPO/KTO `estavel` |
| Testes sem modelo | `pytest modulo-a8/testes -q -m "not modelo"` | todos passam |

Não cole o JSONL `preference-dataset-amplitude.jsonl` do M09. Os pares do lab são originais; o teste `test_pares_originais_nao_citam_arquivo_m09` falha se você reintroduzir nomes daquele arquivo.

## CA8.2 — DPO LoRA no SmolLM2 (CPU)

Modelo padrão: `HuggingFaceTB/SmolLM2-135M`. LoRA `q_proj`/`v_proj`.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Treino rodou | `a8_2.train_loss` | finito; `max_steps` ≥ 1 (padrão 8) |
| API | `a8_2.api` | declara `trl.DPOTrainer` estável |
| Eval TRL no hold-out | `a8_2.eval.eval_rewards/accuracies` e `eval_rewards/margins` | presentes e finitos; **não** são o conjunto de treino |
| Antes vs depois (eval) | `a8_2.avaliacao_eval_base` e `avaliacao_eval_depois` | `preferencia_bruta`, `rewards_accuracies`, `margem_media` |
| Treino separado | `a8_2.avaliacao_treino_depois` | presente (overfit é esperado; não substitui o eval) |
| Aviso TRL de prefixo | `a8_2.aviso_prefixo_trl.ocorreu` | **false** |
| CPU desta trilha | `avaliacao_eval_depois.rewards_accuracies` | **reportado**; se ≤ 0,5, declare — **não invente** e não cole o 0,92 do treino antigo |
| Honestidade | `honestidade.ponto_partida`, `jsonl_m09` | π_SFT ou base; pares originais |
| Testes com modelo | `pytest -q` (marca `modelo`) | passam |

Parágrafo: contraste acurácia **de treino** vs **eval**, e `preferencia_bruta` vs margem implícita. Copiar 0,917 da autoria antiga (treino=eval) zera.

## CA8.3 — família no mesmo lote

| Critério | Campo | Limiar |
| --- | --- | --- |
| Cinco perdas | `a8_3.perdas_no_mesmo_lote_depois_dpo` | `dpo_sigmoid`, `ipo`, `simpo`, `orpo`, `kto` finitos |
| `beta` sem retreino | `a8_3.dpo_vs_beta` | chaves `0.1`, `0.5`, `1.0` |
| Não é ranking | `a8_3.perdas_no_mesmo_lote_depois_dpo.nao_e_ranking` **e** parágrafo | IPO pode ser ≫ DPO no mesmo `h`; unidades diferentes ≠ qualidade |

## CA8.4 — trainers da família (fumaça)

| Critério | Campo | Limiar |
| --- | --- | --- |
| IPO estável | `a8_4.ipo` | `status=ok` **ou** `falhou`/`pulado_env` com `erro`/`api` |
| KTO estável | `a8_4.kto` | idem |
| ORPO experimental | `a8_4.orpo` | `api` contém `experimental` |
| SimPO experimental | `a8_4.simpo` | `api` contém `experimental` |

Um passo de ORPO/SimPO **não** compete com 8 passos de DPO. O item cobra API marcada e `status`, não um ranking de `train_loss`.

## CA8.5 — T4 / harness / IC (não exigido)

| Critério | Campo | Limiar |
| --- | --- | --- |
| Campo presente | `a8_5_t4.status` | `nao_calibrado` **ou** corrida T4 *sua* com GPU no `ambiente` |
| Não inventar | parágrafo | sem IC, sem “harness −2 p.p.”, sem memória T4 se `gpu` é `null` |

## Rubrica rápida (0–10, só CA8)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON reproduzível; split treino/eval; prefixo TRL ausente; accuracies de **eval**; tabela da família com `nao_e_ranking`; parágrafo honesto sobre SFT ausente e T4 |
| 7–8 | Limiares ok; parágrafo vago ou `preferencia_bruta` ignorada |
| 5–6 | JSON de outra pessoa / números digitados; treino pulado sem `SEM_TREINO` declarado |
| 0–4 | Sem JSON; IC/harness inventados; JSONL do M09 republicado; gabarito colado como se fosse medição |

Mesma regra do M09: se no *seu* hardware a acurácia implícita ficar ≤ 0,5, o relatório declara versões, `max_steps` e o número medido. Inventar 0,92 zera o checkpoint.
