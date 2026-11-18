# A11 — MoE, quantização e serving eficiente

**Status:** publicado. **Carga:** ~9 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A2 e A6. **Na prática neste PR:** A2 publicado; A3/A5/A6 ainda esqueleto. MoE é camada avulsa; PTQ ancora no SmolLM2-135M (A2) e no LoRA/NF4 do M09 como ponte conceitual. CA11.3 (LoRA em experts) **não executa**.

Fecha, com aula e lab, o que o tronco só cita: router top-*k*, aux loss / colapso, inspeção de um MoE pequeno real, PTQ INT8/INT4 weight-only, QAT com STE, KV cache e batching medidos, servidores de inferência como leitura.

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A11.1–A11.6 | [`lab/lab_a11.py`](./lab/lab_a11.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA11 | [`checkpoint-ca11.md`](./checkpoint-ca11.md) |
| Mapa do tutor | [`tutor/mapa-a11.md`](./tutor/mapa-a11.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) — **não** use para entregar |
| Corrida de autoria | [`execucao/run-vm.md`](./execucao/run-vm.md) |

## Ambiente

- Python 3.10–3.12, CPU basta para A11.1, A11.5 e os testes sem a marca `modelo`.
- `pip install -r ../requirements.txt` a partir de `curso/trilha-avancada/`.
- A11.4 / A11.6 baixam **SmolLM2-135M** (Apache-2.0), o mesmo do A2. Cache do Hugging Face reaproveita.
- A11.2 tenta **Granite 3.1-1B-A400M-Instruct** (~1,3B, Apache-2.0, 32 experts / top-8). Se não couber: `status=nao_coube` + config. OLMoE-1B-7B: só config nesta CPU.
- Colab T4: não troque o `torch` CUDA pelo wheel CPU. vLLM / OLMoE 4-bit / GGUF continuam **não calibrados** até alguém medir e anexar o JSON.

Variáveis:

```bash
TRILHA_A11_SEM_MOE_REAL=1   # não baixa Granite (config ainda roda)
TRILHA_A11_SEM_SMOL=1       # pula PTQ e KV no SmolLM2
TRILHA_A11_N_NOVOS=8        # tokens gerados nas latências
```

## Como rodar

Na pasta `curso/trilha-avancada/`:

```bash
python modulo-a11/lab/lab_a11.py
python -m pytest modulo-a11/testes -q
python -m pytest modulo-a11/testes -q -m "not modelo"   # sem baixar pesos de 135M de novo
```

Colab (célula):

```python
%cd caminho/para/curso/trilha-avancada
%pip install transformers pytest accelerate safetensors
!python modulo-a11/lab/lab_a11.py
!python -m pytest modulo-a11/testes -q
```

Saída: `modulo-a11/saidas/ca11.json` (gitignore; você entrega o seu). Cópia da autoria: [`execucao/ca11-autoria.json`](./execucao/ca11-autoria.json).

## O que o lab prova

- **A11.1.** 8 experts, top-2; sem aux → colapso (`f_max ≥ 0,50`); com aux → maior entropia e menor `f_max`; conta totais vs ativos.
- **A11.2.** Config Granite 32/8 e OLMoE 64/8; se os pesos do Granite couberem, histograma de uso por domínio e L1 vs permutação. Senão, `nao_coube` documentado.
- **A11.3.** Não executado (A6/T4 ausentes).
- **A11.4.** SmolLM2 fp32 vs INT8 dinâmico (**com** e **sem** `lm_head`) vs INT4 grupo-64 fake-quant: PPL no corpus original, bytes, latência `generate`. GGUF/bnb/NF4 = `nao_calibrado` / leitura M09.
- **A11.5.** MLP `sin(x)`: MSE fp32, PTQ depois, QAT (STE).
- **A11.6.** Atenção prefixo+cache vs sequência cheia (Δ < 1e-5); `use_cache` True/False no SmolLM2; forward batch 1/4/8. vLLM/llama-server = `nao_calibrado`.

Leitura extra opcional (Apache-2.0, **não** vendored): serving/quantização em [lucianoon/llm-course](https://github.com/lucianoon/llm-course).
