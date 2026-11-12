# CA5 — checkpoint (aluno)

Entregue `saidas/ca5.json` + parágrafo. O adapter em `execucao/pi_sft/` é da autoria; o seu lab grava o seu.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Loss caiu | `a5_1.caiu` | true |
| LoRA << denso | `a5_1.n_params_treino` < `a5_1.n_params_total` | true |
| Adapter | `honestidade.pi_sft.encontrado` após o lab | true |
| Eval reportada | `a5_2.eval.acuracia` | presente (pode ser 0) |
| Probes | `a5_3.probes` | duas chaves |
| Testes | `pytest modulo-a5/testes -q` | passam |

T4 / 3 sementes / GSM8K `nao_calibrado` não derruba. Copiar a tabela da aula sem JSON zera.
