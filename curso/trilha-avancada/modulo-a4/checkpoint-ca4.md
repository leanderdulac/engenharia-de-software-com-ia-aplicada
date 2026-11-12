# CA4 — checkpoint (aluno)

Entregue `saidas/ca4.json` + parágrafo.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Template ausente no base | `a4_1.chat_template_no_tokenizer` | false |
| Split | `a4_2.split_ok` | true |
| Máscara | `a4_2.treino_com_system.labels_prompt_menos_100` | true |
| EOS | `a4_2.treino_com_system.todos_eos` | true |
| System custa tokens | `a4_2.delta_n_prompt_system` | > 0 |
| Truncamento corta assistant | `a4_4.trunc_48.truncou` | true |
| Testes | `pytest modulo-a4/testes -q` | passam |

T4 / oasst1 `nao_calibrado` não derruba. Copiar a tabela da aula sem JSON zera.
