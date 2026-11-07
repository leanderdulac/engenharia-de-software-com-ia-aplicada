# Checkpoint opcional de colaboração

Pasta de **fixtures sintéticos** e verificador. O texto ensinável (aluno + instrutor, rubrica, atribuição) está em [`../guia-checkpoint-colaboracao.md`](../guia-checkpoint-colaboracao.md).

Isto **não** substitui C08.x nem C09.x. **Não** é pontuação oficial do Collaborative Intelligence Benchmark.

## Rodar (sem dependência extra, sem API paga)

Na raiz do repositório, Node 22:

```bash
node curso/avaliacao-colaboracao/verificar.mjs curso/avaliacao-colaboracao/evidencias/exemplo-valido.json
node --test curso/avaliacao-colaboracao/verificar.test.mjs
```

Preencha [`evidencias/template.json`](./evidencias/template.json) e aponte o verificador para o seu arquivo.

## Conteúdo

| Caminho | Função |
| --- | --- |
| [`fixtures/`](./fixtures/) | Três tarefas × três versões (sozinho, controle, colaborativo) + gabarito |
| [`evidencias/`](./evidencias/) | Template do aluno e exemplos para o verificador |
| [`verificar.mjs`](./verificar.mjs) | Checagem determinística da evidência JSON |
| [`verificar.test.mjs`](./verificar.test.mjs) | Testes do verificador e dos exemplos |

Todos os registros são didáticos. Nenhum dado pessoal real.
