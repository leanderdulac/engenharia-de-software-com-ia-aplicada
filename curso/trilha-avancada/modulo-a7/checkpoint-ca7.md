# CA7 — checkpoint (aluno)

Entregue `saidas/ca7.json` + parágrafo.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Três acc | `a7_1.acc_direto`, `acc_cot`, `acc_sc` | presentes |
| Flag CoT | `a7_1.cot_piorou` | bool |
| Split | `a7_2.split_ok` | true |
| Testes | `pytest modulo-a7/testes -q` | passam |

GSM8K/IC/T4 `nao_calibrado` não derruba. Acc baixa no 135M **não** zera. Copiar a aula sem JSON zera.
