# Gabarito A1 (instrutor)

Corrida real da VM. Limiares do checkpoint mandam.

## Ambiente

[`../execucao/run-vm.md`](../execucao/run-vm.md). 2026-11-12T14:38:51Z (`epoch_unix=1794494331`), `segundos_total=3.146`.

| Item | Medido |
| --- | --- |
| SmolLM2 `Segurado` | `Seg ur ado` |
| sinistro PT/EN SmolLM2 | 21 / 15, razão **1,40** |
| sinistro PT/EN Qwen | 19 / 14, razão **1,36** |
| greedy = generate | true; texto `"4\n\nA = 1\n"` |
| Δ warpers HF | **0** (T, k, p) |
| T baixa = argmax | true |
| entropia T=0,1…2 | 0,001 / 0,678 / 2,058 / 6,068 / 9,098 nats |
| config | V=49152, d=576, janela=8192, tie=true |
| pytest A1 | 11 passed |

Aluno que copia 1,40 sem JSON próprio está errado. Aluno que diz que top-p “já era o slider do M01” está errado (o tronco é temperature/top-K). Aluno que aponta `razao_pt_en` e `greedy_ids_iguais` do *seu* arquivo está certo.

```bash
python -m pytest modulo-a1/testes -q
```
