# CA3 — checkpoint (aluno)

Entregue `saidas/ca3.json` + parágrafo.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Loss caiu | `a3_1.caiu` | true |
| Acc | `a3_1.acuracia_proximo` | > 0,5 |
| Accumulation | `a3_2.delta_max` | < 1e-5 |
| Envelope | `a3_3.orcamento` | presente |
| Testes | `pytest modulo-a3/testes -q` | passam |

T4 `nao_calibrado` não derruba. Copiar 0,0013 da aula sem JSON zera.
