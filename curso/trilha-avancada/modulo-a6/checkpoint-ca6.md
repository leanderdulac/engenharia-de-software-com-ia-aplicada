# CA6 — checkpoint (aluno)

Entregue `saidas/ca6.json` + parágrafo.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Quatro alvos | `a6_1` length | 4 |
| qv < all_linear | params | `qv.n_treino` < `all_linear.n_treino` |
| Merge | `a6_2.passou` | true (Δ < 1e-3) |
| Multi-adapter | `a6_3.status` | ok |
| GGUF | `a6_4.status` | `nao_calibrado` |
| Testes | `pytest modulo-a6/testes -q` | passam |

T4/Ollama `nao_calibrado` não derruba. Copiar a tabela da aula sem JSON zera.
