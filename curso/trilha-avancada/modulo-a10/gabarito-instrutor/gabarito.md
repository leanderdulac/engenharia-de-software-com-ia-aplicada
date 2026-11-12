# Gabarito A10 (instrutor)

Corrida real da VM. Limiares do checkpoint mandam.

## Ambiente

[`../execucao/run-vm.md`](../execucao/run-vm.md). 2026-11-12T14:27:03Z (`epoch_unix=1794493623`), `segundos_total=27.735`. Licenças `apache-2.0` via `model_info`.

| Item | Medido |
| --- | --- |
| filtro treino | 32/32 |
| professor | 0,917 (55/60), p50 0,146 s, 1447 MB |
| aluno original | 0,600 (36/60), p50 0,045 s, 538 MB |
| sequência 8 passos | **0,650** (39/60), p50 0,052 s |
| logits T=2 8 passos | **0,383** (23/60) — piorou |
| T=4 2 passos | losses 1,87 → 1,83 (fumaça) |
| mesmo tokenizer | true |

Aluno que esconde 0,383 está errado. Aluno que diz “logits sempre ganha” está errado. Aluno que cita a tabela e a licença Apache está certo.

```bash
python -m pytest modulo-a10/testes -q
```
