# Gabarito A8 (instrutor)

Preenchido com a corrida real da VM de autoria. Se o aluno rodar outro `trl` / outros passos, **os limiares do checkpoint mandam**, não estes números literais.

Os dois pares de caderno (`logp_w = −2,0 / −1,5`, …) são pedagogia, não item secreto de CA8. O aluno já os vê em `aula.md` e em `exemplo_numerico_aula()`.

## Ambiente da autoria

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md). CPU, sem CUDA, torch 2.15.0+cpu, transformers 5.22.2, trl 1.17.1, peft 0.21.2, datasets 5.2.0, corrida 2026-11-12T14:02:54Z, `segundos_total=30.536`.

| Item | Medido na autoria | Limiar do aluno |
| --- | --- | --- |
| A8.1 n pares | **12** | ≥ 8 |
| A8.1 chars chosen / rejected | **52,92 / 69,75** (razão **1,32**) | `rejeitado_mais_longo=true` neste dataset |
| A8.1 exemplo DPO / IPO / SimPO / ORPO / KTO | 0,6467 / 17,056 / 1,041 / 0,351 / 0,488 | finitos > 0 |
| A8.1 `dpo_par0` | 0,60265 | — (caderno) |
| A8.2 `train_loss` DPO 8 passos | **0,689866** | finito |
| A8.2 `eval_rewards/accuracies` | **0,916667** | > 0,5 nesta receita; se ≤0,5 no hardware do aluno, declarar |
| A8.2 `eval_rewards/margins` | **0,071216** | finito |
| A8.2 `preferencia_bruta` | **0,500 → 0,500** | não precisa subir; parágrafo tem de notar a discórdia |
| A8.2 margem log-ratio vs base | **0,704376** | presente em `avaliacao_depois` |
| A8.3 mesmo lote DPO/IPO/SimPO/ORPO/KTO | 0,6594 / **19,122** / 0,8347 / 3,101 / 0,4912 | IPO ≫ DPO é esperado (`h` vs `1/(2β)=5`) |
| A8.3 `dpo_vs_beta` 0,1 / 0,5 / 1,0 | 0,6594 / 0,5521 / 0,4680 | mesmos logps; β maior satura σ |
| A8.4 IPO 1 passo `train_loss` | **25,0** | fumaça; não rankear contra DPO-8 |
| A8.4 KTO 2 passos | 0,499373 | `status=ok` ou erro documentado |
| A8.4 ORPO / SimPO 1 passo | 5,736 / 5,75 | `api` contém `experimental` |
| A8.5 T4 | `nao_calibrado` | obrigatório nesta CPU |

Observação da acurácia 0,917: **os 12 pares são o treino**. Não há hold-out. `preferencia_bruta` (soma de logp sem ref) **não** saiu de 0,5. Um parágrafo de aluno que diga “o DPO alinhou o modelo na Amplitude” sem citar overfit / `preferencia_bruta` fica no teto 8. Um que invente IC ou queda de harness zera honestidade.

IPO 25 no 1º passo vs IPO 19 no lote *depois* do DPO: unidades da `(h−5)²` no espaço de soma; o smoke IPO **não** partiu do adapter DPO.

## Como conferir um `ca8.json` entregue

1. Abrir o JSON. Se `ambiente.epoch_unix` for idêntico ao de outro aluno byte a byte **e** o `log_history` também, pedir reexecução.
2. Checar os limiares de [`../checkpoint-ca8.md`](../checkpoint-ca8.md).
3. `honestidade.sft_trilha` declara base, não SFT da trilha. `jsonl_m09` declara pares originais.
4. `a8_5_t4.status=nao_calibrado` enquanto `ambiente.gpu` for `null`. GPU inventada = 0 nesse item.
5. Parágrafo: tem de citar números que existem no JSON (accuracies **e** `preferencia_bruta`, ou comprimento, ou IPO vs DPO no mesmo lote).
6. ORPO/SimPO: a string `experimental` tem de aparecer. `train_loss` menor que o DPO **não** vale ponto extra.

## Erros comuns

| Sintoma | Causa típica | Não faça |
| --- | --- | --- |
| margem 0 depois do DPO | avaliando a política como o próprio ref | peça `modelo_ref` congelado |
| `preferencia_bruta=1` e prosa ainda mais longa | viés de comprimento, não JSON | peça a tabela de chars |
| IPO 19 “pior que DPO 0,66” como ranking | unidades diferentes | relembre `1/(2β)` |
| `train_loss` ORPO vs DPO | 1 passo vs 8; APIs diferentes | cobre só `status` + `experimental` |
| JSONL do M09 no lab | copiou o tronco | os testes de nome falham |
| accuracies 0,917 coladas | não rodou | `epoch_unix` / versões |

## Testes (não estão na aula como gabarito)

```bash
cd curso/trilha-avancada
python -m pytest modulo-a8/testes -q
```

## Números do caderno (iguais à aula)

```
Δ par0 = 1.9     L_DPO par0 ≈ 0.60265
exemplo_aula: dpo=0.64665  ipo=17.056  simpo=1.0407  orpo=0.3511  kto=0.4878
```
