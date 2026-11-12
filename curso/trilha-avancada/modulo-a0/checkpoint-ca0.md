# CA0 — checkpoint objetivo (aluno)

Prática opcional. Não substitui C01–C09. Gabarito do instrutor fora da entrega.

Entregue `saidas/ca0.json` da **sua** máquina e um parágrafo (máx. ½ página).

## CA0.1 — bancada

| Critério | Campo | Limiar |
| --- | --- | --- |
| Ambiente | `ambiente.python`, `pacotes.torch`, `pacotes.transformers` | preenchidos |
| GPU | `ambiente.gpu` | objeto ou `null` |
| Semente | `a0_1.semente` | presente |
| Métricas | `corrida1` p50, p95, tokens_por_s, rss_pico | presentes |
| Repetição | `p50_repetivel_20pct` | **true** (ou parágrafo se o hardware variar mais) |
| Envelope | `orcamento.total_treino_mb` | > 0 |
| Testes | `pytest modulo-a0/testes -q -m "not modelo"` | passam |

## CA0.2 — T4

`nao_calibrado` se `gpu` é null. Não derruba nota.

## Rubrica (0–10)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON próprio; p50 repetível; versões; envelope; parágrafo honesto |
| 7–8 | JSON ok; parágrafo sem apontar campo |
| 5–6 | JSON de outro |
| 0–4 | Sem JSON; inventou tok/s |
