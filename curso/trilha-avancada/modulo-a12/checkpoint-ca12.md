# CA12 — checkpoint (aluno)

Entregue `saidas/ca12.json` + `adr-capstone.md` preenchido.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Duas técnicas | `tecnicas` | inclui A8 e A11 |
| Preferência | `a12_1.base.preferencia_bruta` e `pi_sft` | presentes |
| PTQ | `a12_2.ppl_fp32`, `ppl_int8` | finitos |
| ADR | arquivo com Decisão 1 e 2 apontando o JSON | sim |
| Testes | `pytest modulo-a12/testes -q` | passam |

T4/IC `nao_calibrado` não derruba. Recusar promoção com número vale. Copiar o ADR do M09 zera.
