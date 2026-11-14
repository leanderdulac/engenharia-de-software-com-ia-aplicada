# CA13 — checkpoint (aluno)

Entregue `saidas/ca13.json` + um parágrafo que liga o A5 (treino 1,00 / eval 0,50) à pergunta de 1971, **com os números do seu JSON**.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Shattering | `a13_1.tres_pontos.estilhaça` | true |
| XOR | `a13_1.xor.linearmente_separavel` | false |
| C / margem | `a13_2.linhas` | ≥ 3 valores de C, `margem` e `n_sv` presentes |
| Encoder declarado | `a13_3.encoder_principal` | `smollm2-135m-meanpool` **ou** `tfidf` |
| Classificadores | `a13_3.tfidf.svm_linear`, `svm_rbf`, `logreg` | `acc_treino` e `acc_eval` |
| Zhang | `a13_4.rotulos_aleatorios` | svm e mlp com treino e eval |
| Ponte A5 | `a13_5.termo_lora.vacuo` | true |
| Frase obrigatória | parágrafo | afirma que VC **não** é a teoria de generalização dos LLMs |
| Testes | `pytest modulo-a13/testes -q -m "not modelo"` | passam |

T4 `nao_calibrado` não derruba. Usar TF-IDF com o encoder declarado não derruba. Dizer que o LoRA tem VC = 460 800 **zera** (é proxy, o JSON avisa). Copiar a tabela da aula sem JSON zera.
