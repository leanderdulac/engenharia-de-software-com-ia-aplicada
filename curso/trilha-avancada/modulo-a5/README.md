# A5 — SFT sério

**Status:** publicado. **Carga:** ~6 h. **Pré-req:** A3, A4.

Fecha: loss só no assistant, LoRA, π_SFT em `execucao/pi_sft/`, probes de esquecimento, tracking no JSON. GSM8K/Dolly/T4/`nao_calibrado`. A8/A9/A10 reusam o adapter (`TRILHA_PI_SFT=0` desliga).

```bash
python modulo-a5/lab/lab_a5.py
python -m pytest modulo-a5/testes -q
```

Saída: `modulo-a5/saidas/ca5.json`. Autoria: [`execucao/ca5-autoria.json`](./execucao/ca5-autoria.json). Adapter: [`execucao/pi_sft/`](./execucao/pi_sft/).

- Aula [`aula.md`](./aula.md) · CA [`checkpoint-ca5.md`](./checkpoint-ca5.md) · tutor [`tutor/mapa-a5.md`](./tutor/mapa-a5.md) · gabarito [`gabarito-instrutor/`](./gabarito-instrutor/)
