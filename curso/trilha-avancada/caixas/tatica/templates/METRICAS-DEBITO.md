# Métricas de débito deste brinquedo

Contas do lab, não um painel de produção.

| Métrica | Como o script conta |
| --- | --- |
| entregues | features cujo teste congelado ficou verde. Nos três modos o fallback limpo existe, então o número é 8 |
| violações | diffs ruins que entraram no `api.py` |
| duplicação | funções de `api.py` que copiam a lista do registro ou o corpo de `gravar` |
| custo da feature seguinte | `4 + 1 × violações`. O 4 é o custo limpo. O 1 é a multa por débito já acumulado |
| passos | soma do que esta leva gastou, já com a multa do débito anterior |
| atalhos tentados / aceitos | o plano da seed, e quantos desses diffs entraram |
| barrados pelo teste | o bug tático, igual nos três modos |
| disparos da regra | a regra mecânica falou |
| recusas do revisor | `recusar` ou `escalar` |

A série ao longo do tempo, neste script, é a seed: cada feature vê o débito das anteriores. Não há um histórico de meses.
