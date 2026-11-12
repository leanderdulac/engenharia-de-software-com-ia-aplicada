# Gabarito A2 (instrutor)

Preenchido com a corrida real da VM de autoria. Se o aluno rodar outro `transformers` / outro id de modelo, **os limiares do checkpoint mandam**, não estes números literais.

Os tensores 2×2 da aula são pedagogia, não item secreto de CA2. O aluno já os vê em `aula.md` e em `exemplo_numerico.py`.

## Ambiente da autoria (preencher após `lab_a2.py`)

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md) — colado da stdout real, sem edição de métricas.

Esperado nesta VM (CPU, SmolLM2-135M, transformers 5.22.2, torch 2.15.0+cpu), corrida 2026-11-12T13:39:35Z — ver [`../execucao/run-vm.md`](../execucao/run-vm.md):

| Item | Medido na autoria | Limiar do aluno |
| --- | --- | --- |
| A2.1 Δ vs SDPA | **2.384185791015625e-07** | < 1e-5 |
| A2.1 causal_ok | true | true |
| Exemplo 2×2 Δ | 2.384185791015625e-07 | — (não é CA) |
| `num_parameters` SmolLM2-135M | **134515008** (erro relativo 0) | ≤ 0,1% |
| por componente | emb 28311552, attn 26542080, ffn 79626240, norm 35136, lm_head 0 | soma = total |
| GQA | Q=9, KV=3, d=576, L=30, silu, rope_θ=100000 | config coerente |
| Δ bloco 0 vs hidden_states[1] | **0.0** | < 1e-3 |
| Δ mapa vs `output_attentions` | **0.0** | mapa triangular |

Observação do mapa (camada 0, cabeça 0, *não* é gabarito único — outras cabeças diferem): na primeira camada a massa é espalhada no prefixo, não um “salto” nítido de `ABC` para `Placa`. Um parágrafo de aluno que descreva a diagonal/causal e um token concreto do JSON está correto; um que invente “a cabeça 0 só olha a placa” está errado neste mapa.

## Como conferir um `ca2.json` entregue

1. Abrir o JSON. Se `ambiente.epoch_unix` for idêntico ao de outro aluno byte a byte **e** o mapa também, pedir reexecução com `TRILHA_A2_FRASE` diferente.
2. Checar os quatro booleanos / limiares de [`../checkpoint-ca2.md`](../checkpoint-ca2.md).
3. `a2_2.tokens` tem de tokenizar a frase declarada (não precisa ser o mesmo tokenizer split da autoria se o id do modelo mudou).
4. Parágrafo: tem de citar tokens que existem no JSON. “A cabeça olhou a placa” sem apontar índice = teto 8.

## Erros comuns

| Sintoma | Causa típica | Não faça |
| --- | --- | --- |
| Δ ~ 0.1–1 no bloco | pós-norma em vez de pré-norma | revelar a ordem; pergunte o diagrama |
| Δ grande só na atenção | esqueceu repetir KV no GQA | peça `k_proj.out_features` vs `hidden_size` |
| Δ grande, atenção ok | pulou RoPE | peça se `cos/sin` entraram |
| contagem +50% | somou `lm_head` amarrado | `id(p)` |
| mapa não triangular | `is_causal=False` ou SDPA com `output_attentions` | `attn_implementation=eager` |
| NaN no softmax | máscara 0 em vez de −∞ | — |

## Testes ocultos (não estão na aula)

Os arquivos em `testes/test_causal.py` já incluem o controle “sem máscara o futuro vaza”. Se o aluno entregar só o JSON sem pytest, rode você:

```bash
cd curso/trilha-avancada
python -m pytest modulo-a2/testes -q
```

## Números do exemplo 2×2 (iguais à aula)

```
pesos pos1 = [0.33023846, 0.66976154]
saída pos1 = [2.33952308, 3.33952308]
LayerNorm([1,2,3]) ≈ [-1.22473562, 0, 1.22473562]
RMSNorm([1,2,3])  ≈ [0.46290955, 0.92581910, 1.38872862]
```
