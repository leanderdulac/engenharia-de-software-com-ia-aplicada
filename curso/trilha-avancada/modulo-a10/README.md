# A10 — Destilação

**Status:** publicado. **Carga:** ~6 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A5 e A7. **Na prática neste PR:** A9 publicado; A5/A7 esqueleto. Aluno = SmolLM2-135M **base** + LoRA. Professor = SmolLM2-360M (Apache-2.0, mesmo tokenizer). Qwen2.5-0.5B é Apache-2.0 mas vocabulário diferente — citado, não baixado.

Fecha: professor/aluno, destilação por resposta e por logits (T + KL), features (aula), self-distillation e reasoning distillation (aula), sintético + verificador, LoRA, retenção (declarada não medida), qualidade × latência × memória, licença dos dados gerados.

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A10.1–A10.6 | [`lab/lab_a10.py`](./lab/lab_a10.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA10 | [`checkpoint-ca10.md`](./checkpoint-ca10.md) |
| Mapa do tutor | [`tutor/mapa-a10.md`](./tutor/mapa-a10.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) |
| Corrida de autoria | [`execucao/run-vm.md`](./execucao/run-vm.md) |

## Ambiente

- CPU basta. Baixa **SmolLM2-360M** (~1,4 GB fp32) além do 135M.
- `pip install -r ../requirements.txt`
- Colab T4: não troque o `torch` CUDA. Custo/1k = **não calibrado**.

```bash
TRILHA_A10_PASSOS=8
TRILHA_A10_N_EVAL=60
TRILHA_A10_SEM_DESTILAR=1   # só gera/filtra
```

```bash
cd curso/trilha-avancada
python modulo-a10/lab/lab_a10.py
python -m pytest modulo-a10/testes -q
```

Saída: `modulo-a10/saidas/ca10.json` (gitignore). Autoria: [`execucao/ca10-autoria.json`](./execucao/ca10-autoria.json).

## O que o lab prova

- **A10.1.** Professor gera 32 treinos; filtro 32/32; eval hold-out n=60 acc **0,917**, p50 0,146 s, 1447 MB.
- **A10.2.** Aluno original acc **0,600**, p50 0,045 s, 538 MB.
- **A10.3.** Destilação por resposta (CE, 8 passos LoRA) → acc **0,650**.
- **A10.4.** Destilação por logits T=2 (8 passos) → acc **0,383** (piorou; a aula não esconde).
- **A10.4b.** Fumaça T=4 (2 passos).
- **A10.6.** `nao_calibrado` (T4).
