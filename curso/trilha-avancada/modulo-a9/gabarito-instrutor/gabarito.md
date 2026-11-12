# Gabarito A9 (instrutor)

Corrida real da VM de autoria. Limiares do checkpoint mandam, não estes literais.

## Ambiente

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md). CPU, torch 2.15.0+cpu, trl 1.17.1, 2026-11-12T14:23:03Z (`epoch_unix=1794493383`), `segundos_total=68.589`.

| Item | Medido | Limiar |
| --- | --- | --- |
| REINFORCE p* | 0,972 / 0,982 | p* > 0,25 |
| Hacking n_div | **2** | ≥ 1 |
| split | 24 / **80**, disjuntos | n_eval ≥ 50 |
| eval base | **0,600** (48/80) | reportar |
| seeds 0/1/2 depois | 0,738 / 0,725 / 0,738 (59 / 58 / 59) | 3 seeds |
| delta média ± desvio | **+0,133 ± 0,007** | `melhorou_claro` |
| treino 17/24 → 21/24 | nas 3 seeds | eval manda |
| zero-std (fração) | 0,31 / 0,25 / 0,06 → **0,21 ± 0,13** | reportar |
| beta 0,04 | `kl_max≈0,016`, 15/16 ≠ 0; eval 0,738 | kl_n_nao_zero ≥ 1 |
| hack vs exata n=20 | 1,0 vs 0,35 | os dois |
| T4 | `nao_calibrado` | se gpu null |

Aluno com n_eval=4 (versão antiga) não cumpre CA9.3. Aluno que trata +0,13 em n=80 e 3 seeds como IC 95% perde o item de honestidade, não o de treino.

```bash
python -m pytest modulo-a9/testes -q
```
