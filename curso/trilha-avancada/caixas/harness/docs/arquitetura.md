# Arquitetura do brinquedo

Doze funções de sinistro em [`brinquedo/funcoes.py`](../brinquedo/funcoes.py). Duas pastas:

- `rotas/` — único lugar em que a migração v1→v2 pode escrever.
- `db/` — leitura. Configuração e dados não são do agente.

O «agente» desta caixa é o script [`lab/simular.py`](../lab/simular.py). Não é um modelo. Não chama API.
