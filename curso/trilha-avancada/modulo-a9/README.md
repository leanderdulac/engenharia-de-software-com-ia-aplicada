# A9 — RL com recompensa verificável

**Status:** publicado. **Carga:** ~8 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A7 e A8. **Na prática:** A8 publicado; A5 publicado (π_SFT opcional, `TRILHA_PI_SFT=0` no pytest); A7/A6 esqueleto. O demo GRPO do M09 **não** é copiado e **não** atualiza pesos; este lab chama `GRPOTrainer.train()`.

Fecha: política/ação/recompensa, on/off-policy, REINFORCE, PPO (clip, vantagem), GRPO (vantagem no grupo, `beta` KL), recompensa verificável, credit assignment, reward hacking, instabilidade, SFT × DPO × PPO × GRPO.

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A9.1–A9.5 | [`lab/lab_a9.py`](./lab/lab_a9.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA9 | [`checkpoint-ca9.md`](./checkpoint-ca9.md) |
| Mapa do tutor | [`tutor/mapa-a9.md`](./tutor/mapa-a9.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) — **não** use para entregar |
| Corrida de autoria | [`execucao/run-vm.md`](./execucao/run-vm.md) |

## Ambiente

- Python 3.10–3.12, CPU basta (REINFORCE + GRPO G=2, 3 passos).
- `pip install -r ../requirements.txt` (`trl`, `peft`, `datasets`).
- SmolLM2-135M (Apache-2.0), o mesmo do A2/A8/A11.
- Colab T4: não troque o `torch` CUDA. G grande / IC = **não calibrado**.

```bash
TRILHA_A9_PASSOS=16
TRILHA_A9_G=4
TRILHA_A9_SEEDS=0,1,2
TRILHA_A9_N_EVAL=80
TRILHA_A9_SEM_GRPO=1    # só bandit + hacking
TRILHA_A9_SEM_BETA=1    # não compara beta>0
```

## Como rodar

```bash
cd curso/trilha-avancada
python modulo-a9/lab/lab_a9.py
python -m pytest modulo-a9/testes -q
python -m pytest modulo-a9/testes -q -m "not modelo"
```

Saída: `modulo-a9/saidas/ca9.json` (gitignore). Autoria: [`execucao/ca9-autoria.json`](./execucao/ca9-autoria.json).

## O que o lab prova

- **A9.1.** REINFORCE bandit 4 ações; com/sem baseline; `p(ótima)` sobe.
- **A9.2.** Mesmas compleções: primeiro inteiro vs formato vs hack de dígito; `"0"` e `"70"` divergem.
- **A9.3.** `GRPOTrainer` **atualiza** LoRA (`beta=0`, G=4, 16 passos, **3 seeds**). Eval hold-out n=80 **antes/depois**. Nesta CPU: 0,600 → **0,733 ± 0,007** (48/80 → 58–59/80). ~1/5 dos passos ainda tem `frac_reward_zero_std=1`.
- **A9.4.** `beta=0.04` nos mesmos 16 passos; `kl` não nulo (máx. ≈0,016). Hack vs exata no base (1,0 vs 0,35 em n=20).
- **A9.5.** `nao_calibrado` (T4).
