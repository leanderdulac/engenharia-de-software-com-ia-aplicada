# Gabarito A10 (instrutor)

Corrida real da VM. Limiares do checkpoint mandam.

## Ambiente

[`../execucao/run-vm.md`](../execucao/run-vm.md). 2026-11-12T14:33:51Z (`epoch_unix=1794494031`), `segundos_total=30.07`. Licenças `apache-2.0` via `model_info`.

| Item | Medido |
| --- | --- |
| filtro treino | 32/32 |
| professor | 0,917 (55/60), p50 0,108 s, 1447 MB |
| aluno original | 0,600 (36/60), p50 0,045 s, 538 MB |
| sequência 8 passos | **0,650** (39/60), p50 0,044 s |
| logits T=2 8 passos | **0,383** (23/60) — piorou |
| diagnóstico | `shift_alinhado=true`, `mascara_inclui_prompt=false`, `t2_bate=true`, `n_complecao=8`, `razao_t2=4,0` |
| mista α=0,5 | **0,567** (34/60) — mitiga, não vence CE nem o base |
| T=4 2 passos | losses 1,87 → 1,83 (fumaça) |
| mesmo tokenizer | true |

Máscara, shift e T² estavam certos. A queda dos logits **não** é bug desses três. Compleção do professor tem 8 tokens (`"0 1+1=2 "`): o verificador só olha o primeiro inteiro; KL casa |V|=49 152 também no lixo. LoRA r=8, 8 passos. Mista recupera (0,383 → 0,567) e ainda fica abaixo do aluno original (0,600) e da sequência (0,650).

Aluno que esconde 0,383 ou 0,567 está errado. Aluno que diz “logits sempre ganha” ou “era a máscara” sem abrir o `diagnostico` está errado. Aluno que cita a tabela, o diagnóstico e a licença Apache está certo.

```bash
python -m pytest modulo-a10/testes -q
```
