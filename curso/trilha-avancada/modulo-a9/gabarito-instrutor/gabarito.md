# Gabarito A9 (instrutor)

Corrida real da VM de autoria. Limiares do checkpoint mandam, não estes literais.

## Ambiente

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md). CPU, torch 2.15.0+cpu, trl 1.17.1, 2026-11-12T14:16:19Z (`epoch_unix=1794492979`), `segundos_total=10.742`.

| Item | Medido | Limiar |
| --- | --- | --- |
| REINFORCE com baseline início→fim | 0,40 → **1,00**, p*=**0,972** | `subiu` |
| REINFORCE sem baseline | 0,40 → **1,00**, p*=**0,982** | p* > 0,25 |
| Hacking n_div | **2** (`"0"`, `"70"`) | ≥ 1 |
| GRPO `atualiza_pesos` | **true**, 3 passos, G=2, β=0 | true |
| `rewards_log` | `[0,5, 0,5, 0,0]` | finito |
| `grad_norm` (passos 1–3) | 0,67 / 1,10 / 0 | LoRA mexeu nos dois primeiros |
| `frac_reward_zero_std` | `[0, 0, 1]` | passo 3 homogêneo |
| eval antes/depois | **0,50 → 0,75** (2/4 → 3/4) | reportar |
| treino antes/depois | 0,875 → 0,875 (7/8) | — |
| flip eval | `7+1=`: `"10\n\nA."` → `"8\n\nA. "` | um exemplo, não IC |
| `por_que_nao_subiu` | **null** (eval subiu) | preenchido só se não subir |
| beta 0,04 1 passo | `ok`, `kl_log=[0.0]`, `train_loss≈9,9e-9` | kl presente |
| hack vs exata no base | **1,0 vs 0,5** | os dois |
| T4 | `nao_calibrado` | se gpu null |

O GRPO **treinou** (LoRA, `train()`, `grad_norm` ≠ 0 nos passos 1–2). Aluno que escreve “GRPO não atualiza pesos” está errado. Aluno que trata 3/4 em n=4 como IC está errado. Aluno que cita o flip `7+1=` e o passo 3 com `frac_reward_zero_std=1` está certo.

Prompt **sem** `\n` depois de `=`. Recompensa = primeiro inteiro, não a string inteira.

O demo M09 **não** substitui CA9.3.

```bash
python -m pytest modulo-a9/testes -q
```
