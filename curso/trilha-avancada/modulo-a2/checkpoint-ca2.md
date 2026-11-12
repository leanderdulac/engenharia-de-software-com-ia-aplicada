# CA2 — checkpoint objetivo (aluno)

Prática **opcional** da trilha. Não substitui C01–C09. Não vale para a média das 240 h salvo o regulamento da turma decidir depois.

Entregue um único pacote:

1. `saidas/ca2.json` gerado por `python modulo-a2/lab/lab_a2.py` **na sua máquina** (ou Colab). Não reescreva os números à mão.
2. Um parágrafo (máx. 1 página) apontando campos do JSON. Sem print sem arquivo.

O gabarito do instrutor **não** faz parte desta entrega. Se você abriu `gabarito-instrutor/`, declare.

## CA2.1 — atenção do zero

| Critério | Como o instrutor confere | Limiar |
| --- | --- | --- |
| Implementação bate com PyTorch | `a2_1.diff_max_vs_sdpa` | **< 1e-5** |
| Futuro não vaza | `a2_1.causal_ok` | **true** |
| Testes da pasta | `pytest modulo-a2/testes -q -m "not modelo"` | todos passam |

Não cole o código de `atencao.py` “como se fosse seu” se você não rodou. O artefato é o JSON + os testes no seu ambiente.

## CA2.2 — um bloco real

Modelo padrão: `HuggingFaceTB/SmolLM2-135M`. Outro id Apache-2.0 da mesma família (Qwen2.5-0.5B) vale se o JSON declarar o id e os limiares abaixo ainda forem atingidos.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Config lida (camadas, Q, KV, GQA, act, RoPE, d) | `a2_2.config` | todos os campos presentes |
| Contagem vs `num_parameters()` | `a2_2.parametros.erro_relativo` | **≤ 0,001** (0,1%) |
| Bloco reconstruído vs `hidden_states[camada+1]` | `a2_2.bloco_reconstruido.diff_max` | **< 1e-3** (fp32) |
| Mapa causal | `a2_2.atencao.causal_ok` | **true** |
| Frase e tokens | `a2_2.frase`, `a2_2.tokens` | não vazios |
| Testes com modelo | `pytest -q` (marca `modelo`) | passam |

Parágrafo obrigatório: escolha **uma** posição de consulta no mapa da cabeça 0 e diga, com os tokens do JSON, para quais chaves a massa foi. Se o mapa estiver uniforme ou concentrado na diagonal, escreva isso — resultado negativo medido vale.

## Rubrica rápida (0–10, só CA2)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON reproduzível; os quatro limiares; pytest verde; parágrafo ancorado em tokens reais |
| 7–8 | Limiares ok; parágrafo vago ou ambiente pela metade documentado |
| 5–6 | JSON de outra pessoa / números digitados; modelo não rodou |
| 0–4 | Sem JSON; limiar furado sem explicação; gabarito colado como se fosse medição |

Mesma regra do M09: se no *seu* hardware o Δ do bloco ficar acima de 1e-3, o relatório declara versões, dtype e o Δ medido. Inventar 0.0 zera o checkpoint.
