# A13 — Generalização clássica: Vapnik, VC e SVM — e onde ela falha em LLMs

**Status:** publicado. **Carga:** ~4 h. **Pré-req:** A5. **Opcional extra:** fora das 78 h de A0–A12 e das 240 h de M01–M09.

ERM, convergência uniforme, VC via shattering, bound vácuo, SRM, margem, vetores de suporte, kernel, soft-margin C. Contraste Zhang et al. 2017. **VC não é a teoria de generalização dos LLMs.** SVM hoje: baseline sobre embeddings, classificador leve, guardrail raso.

```bash
python modulo-a13/lab/lab_a13.py
# sem SmolLM2 (só TF-IDF):
TRILHA_A13_EMBED=0 python modulo-a13/lab/lab_a13.py
python -m pytest modulo-a13/testes -q -m "not modelo"
```

Saída: `modulo-a13/saidas/ca13.json`. Autoria: [`execucao/ca13-autoria.json`](./execucao/ca13-autoria.json).

- Aula [`aula.md`](./aula.md) · CA [`checkpoint-ca13.md`](./checkpoint-ca13.md) · tutor [`tutor/mapa-a13.md`](./tutor/mapa-a13.md) · gabarito [`gabarito-instrutor/`](./gabarito-instrutor/) · refs [`referencias.md`](./referencias.md)
