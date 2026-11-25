# A0 — Bancada: ambiente, medição e orçamento de GPU

**Status:** publicado. **Carga:** ~2 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito:** M09 com C09.3 e C09.4. **Na prática:** CPU; T4 `nao_calibrado`. Instruct 0,5B não baixado — SmolLM2-135M.

Fecha: versões, semente, p50/p95, tokens/s, RSS, envelope de memória, `bancada.json` (= `ca0.json`).

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Lab A0.1 | [`lab/lab_a0.py`](./lab/lab_a0.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA0 | [`checkpoint-ca0.md`](./checkpoint-ca0.md) |
| Mapa do tutor | [`tutor/mapa-a0.md`](./tutor/mapa-a0.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito | [`gabarito-instrutor/`](./gabarito-instrutor/) |
| Corrida | [`execucao/run-vm.md`](./execucao/run-vm.md) |

```bash
cd curso/trilha-avancada
python modulo-a0/lab/lab_a0.py
python -m pytest modulo-a0/testes -q
```

Saída: `modulo-a0/saidas/ca0.json`. Autoria: [`execucao/ca0-autoria.json`](./execucao/ca0-autoria.json).

## O que o lab prova

- **A0.1.** 20 gerações greedy, 8 tokens. p50 **0,172 s** / **0,163 s** (repetível ±20%). **46 tok/s**. Envelope treino **2152 MB**. bitsandbytes ausente. T4 `nao_calibrado`.
