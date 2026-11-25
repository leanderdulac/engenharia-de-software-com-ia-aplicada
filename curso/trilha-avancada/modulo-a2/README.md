# A2 — O bloco Transformer, peça por peça

**Status:** publicado. **Carga:** ~6 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A1. **Na prática neste PR:** M09 feito + noção de token/amostragem do M01 (A1 ainda é esqueleto).

Fecha, com aula e lab, o que o tronco não ensina: do id de token até o fluxo de um bloco decoder-only (atenção causal, Q/K/V, produto interno escalado, multi-cabeça, máscaras, posição, FFN, resíduo, norma).

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A2.1 e A2.2 | [`lab/lab_a2.py`](./lab/lab_a2.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA2 | [`checkpoint-ca2.md`](./checkpoint-ca2.md) |
| Mapa do tutor | [`tutor/mapa-a2.md`](./tutor/mapa-a2.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) — **não** use para entregar |

## Ambiente

- Python 3.10–3.12, CPU basta.
- `pip install -r ../requirements.txt` a partir de `curso/trilha-avancada/`.
- Lab A2.2 baixa **SmolLM2-135M** (~270 M parâmetros, Apache-2.0). Primeira corrida precisa de rede. Depois usa o cache do Hugging Face.
- Opcional, mais pesado: `TRILHA_A2_MODELO=Qwen/Qwen2.5-0.5B`.
- Colab gratuito (T4): o runtime já tem CUDA; instale `transformers pytest accelerate safetensors` e **não** troque o `torch` do Colab pelo wheel CPU.

## Como rodar

Na pasta `curso/trilha-avancada/`:

```bash
python modulo-a2/lab/lab_a2.py
python -m pytest modulo-a2/testes -q
python modulo-a2/lab/exemplo_numerico.py   # números da aula, conferidos
```

Colab (célula):

```python
# clone o repo da turma, depois:
%cd caminho/para/curso/trilha-avancada
%pip install transformers pytest accelerate safetensors
!python modulo-a2/lab/lab_a2.py
!python -m pytest modulo-a2/testes -q
```

Saída do lab: `modulo-a2/saidas/ca2.json` (gitignore; você entrega o seu).

## O que o lab prova

- **A2.1.** Atenção causal em PyTorch puro vs `torch.nn.functional.scaled_dot_product_attention`; Δ máximo < 1e-5; mudar o token *futuro* não altera as posições anteriores.
- **A2.2.** Config do modelo real (camadas, Q vs KV, GQA, RoPE, RMSNorm, SwiGLU); contagem de parâmetros vs `num_parameters()` (±0,1%); um bloco reconstruído vs o `hidden_state` da mesma camada (Δ < 1e-3 em fp32); mapa de atenção de uma frase no espírito Amplitude.

Leitura extra opcional (Apache-2.0, **não** está no recorte vendored): módulo 02 de [lucianoon/llm-course](https://github.com/lucianoon/llm-course). Há um MiniGPT em [`referencia/llm-course/tools/minigpt.py`](../../../referencia/llm-course/tools/minigpt.py) — código, sem a aula deste A2.
