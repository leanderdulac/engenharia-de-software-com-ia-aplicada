# CA14 — checkpoint (aluno)

Entregue `saidas/ca14.json` + um parágrafo que liga o IC do A5 (n=2, acc 0,50) ao bound vácuo do A13, **com os números do seu JSON**.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Ponte A5/A7/A13 | `a14_1.a5_eval_n2.n` | 2 (não inventar n=6 no A5) |
| Wilson largo | `a14_1.a5_eval_n2.vacuo_pratico` | true |
| n=6 declarado | `a14_1.a13_zhang_svm_n6.n` **ou** `a5_se_n6` | 6, origem explícita |
| Vazamento | `a14_2` e `a14_3` | `delta_otimista` presente |
| Duplicata | `a14_3.otimista` | true |
| k-fold | `a14_4.accs` | 5 valores |
| Complexidade | `a14_5.polinomio.linhas`, `knn.linhas` | ≥ 4 graus / ≥ 3 k |
| Interpolação | `a14_6.pico_p` | presente |
| Testes | `pytest modulo-a14/testes -q -m "not modelo"` | passam |

T4 `nao_calibrado` não derruba. Afirmar que o A5 mediu n_eval=6 **zera**. Copiar texto do livro Lindholm (ou dizer que a aula é adaptação dele) **zera**.
