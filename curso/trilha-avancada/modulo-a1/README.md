# A1 — Por dentro do LLM: tokens, logits e amostragem

**Status:** publicado. **Carga:** ~4 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A0. **Na prática neste PR:** A0 ainda é esqueleto. Ponte: M01 (sliders de temperature/top-K) + A2 já publicado (o bloco). O JSON declara isso.

Fecha: evolução curta até foundation models; BPE e custo PT vs EN; embedding de token; janela; laço autorregressivo; logits→softmax; temperature, top-k, top-p, greedy; treino ≠ forward ≠ geração. Top-p **não** é aula no tronco.

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A1.1 e A1.2 | [`lab/lab_a1.py`](./lab/lab_a1.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA1 | [`checkpoint-ca1.md`](./checkpoint-ca1.md) |
| Mapa do tutor | [`tutor/mapa-a1.md`](./tutor/mapa-a1.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) — **não** use para entregar |
| Corrida de autoria | [`execucao/run-vm.md`](./execucao/run-vm.md) |

## Ambiente

- Python 3.10–3.12, CPU basta.
- `pip install -r ../requirements.txt` a partir de `curso/trilha-avancada/`.
- A1.1 baixa **tokenizers** SmolLM2-135M e Qwen2.5-0.5B (sem os pesos do Qwen).
- A1.2 carrega **SmolLM2-135M** (~270 M, Apache-2.0).
- Colab T4: não troque o `torch` CUDA. Prompt API / custo/1k = **não calibrado**.

```bash
cd curso/trilha-avancada
python modulo-a1/lab/lab_a1.py
python -m pytest modulo-a1/testes -q
python -m pytest modulo-a1/testes -q -m "not modelo"
```

Saída: `modulo-a1/saidas/ca1.json` (gitignore). Autoria: [`execucao/ca1-autoria.json`](./execucao/ca1-autoria.json).

## O que o lab prova

- **A1.1.** Três tokenizers (SmolLM2, Qwen2.5-0.5B, caracteres). Par “sinistro”: SmolLM2 **21** tok PT vs **15** EN (razão **1,40**). `Segurado` → `Seg ur ado`.
- **A1.2.** Softmax/temperatura/top-k/top-p do zero; Δ vs warpers HF **0**; greedy manual = `generate(do_sample=False)`; entropia sobe com T (0,001 → 9,10 nats).
