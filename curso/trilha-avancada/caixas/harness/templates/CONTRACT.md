# CONTRACT

Pedido explícito. O harness torna isto um fato (arquivo versionado), não um parágrafo no chat.

```yaml
goal: Migrar as 12 funções de sinistro de v1 para v2 (snake_case), sem inventar regra que o contrato não tenha.
output: cada função v2 em rotas/, com o par (nome v1, nome v2) de brinquedo/funcoes.py
scope: rotas/ e o PROGRESS.md desta pasta
never:
  - escrever em db/
  - editar o teste que julga a migração
  - reescrever o JSONL de eval do M09
  - inventar decisão de streaming para export_claims
done_when:
  - o sensor (pytest do brinquedo) está verde nas funções do escopo
  - export_claims está em blocked, não em done
  - o relatório repete o número do sensor, não a impressão do construtor
```

Liga ao curso: máscara só no assistente (A4) e eval congelado (A14) são o mesmo tipo de `never`.
