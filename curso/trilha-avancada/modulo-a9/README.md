# A9 — RL com recompensa verificável

**Status:** publicado. **Carga:** ~8 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A7 e A8. **Na prática neste PR:** A8 publicado; A7/A5/A6 esqueleto. GRPO ancora no SmolLM2-135M **base** + LoRA. O demo GRPO do M09 **não** é copiado e **não** atualiza pesos; este lab chama `GRPOTrainer.train()`.

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
TRILHA_A9_PASSOS=3
TRILHA_A9_SEM_GRPO=1    # só bandit + hacking
TRILHA_A9_SEM_BETA=1    # não roda o 1 passo com beta>0
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
- **A9.3.** `GRPOTrainer` **atualiza** LoRA (`beta=0`, G=2, 3 passos). Eval hold-out **antes/depois**. Nesta CPU: 0,50 → 0,75 (2/4 → 3/4); treino 7/8 → 7/8. Prompt termina em `=`; recompensa = primeiro inteiro.
- **A9.4.** Fumaça `beta=0.04` (chave `kl` no log) + hack vs exata **no base** (1,0 vs 0,5).
- **A9.5.** `nao_calibrado` (T4).
