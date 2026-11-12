# A8 — Alinhamento por preferências

**Status:** publicado. **Carga:** ~7 h. **Trilha:** opcional, fora das 240 h.

**Pré-requisito oficial (plano):** A5 e A6. **Na prática:** A5 publicado — DPO parte de **π_SFT** se `modulo-a5/execucao/pi_sft/adapter_config.json` existir (`TRILHA_PI_SFT=0` força o SmolLM2-135M **base**). A6 ainda esqueleto. Pares originais no *padrão* do M09 (JSON vs prosa / vírgula decimal), sem copiar o JSONL do tronco. CA8.5 (T4 + IC + harness) **não executa**.

Fecha, com aula e lab, o que o tronco só cita: par `chosen`/`rejected`, reward model, RLHF/RLAIF, DPO com derivação, família (IPO, SimPO, ORPO, KTO), `beta`, viés de comprimento, SFT vs preferência, avaliação por rewards/accuracies.

| Peça | Onde |
| --- | --- |
| Aula | [`aula.md`](./aula.md) |
| Labs A8.1–A8.5 | [`lab/lab_a8.py`](./lab/lab_a8.py) |
| Testes | [`testes/`](./testes/) |
| Checkpoint CA8 | [`checkpoint-ca8.md`](./checkpoint-ca8.md) |
| Mapa do tutor | [`tutor/mapa-a8.md`](./tutor/mapa-a8.md) |
| Referências | [`referencias.md`](./referencias.md) |
| Gabarito (instrutor) | [`gabarito-instrutor/`](./gabarito-instrutor/) — **não** use para entregar |
| Corrida de autoria | [`execucao/run-vm.md`](./execucao/run-vm.md) |

## Ambiente

- Python 3.10–3.12, **CPU basta** para A8.1–A8.4 (8 passos DPO + fumaça da família).
- `pip install -r ../requirements.txt` a partir de `curso/trilha-avancada/` (inclui `trl`, `peft`, `datasets`).
- Baixa **SmolLM2-135M** (Apache-2.0), o mesmo do A2/A11. Cache do Hugging Face reaproveita.
- Colab T4: não troque o `torch` CUDA pelo wheel CPU. Harness Amplitude, IC de `rewards/accuracies` e tabela método×memória×tempo na T4 continuam **não calibrados** até alguém medir e anexar o JSON.

Variáveis:

```bash
TRILHA_A8_PASSOS=8              # passos do DPO sigmoid (CPU)
TRILHA_A8_PASSOS_KTO=2          # passos do KTOTrainer
TRILHA_A8_SEM_TREINO=1          # só comprimento + perdas no papel (sem SmolLM2)
TRILHA_A8_SEM_EXPERIMENTAL=1    # não instancia ORPO/SimPO
TRILHA_A8_SEM_KTO=1             # não instancia KTOTrainer
```

## Como rodar

Na pasta `curso/trilha-avancada/`:

```bash
python modulo-a8/lab/lab_a8.py
python -m pytest modulo-a8/testes -q
python -m pytest modulo-a8/testes -q -m "not modelo"   # sem baixar pesos de 135M
```

Colab (célula):

```python
%cd caminho/para/curso/trilha-avancada
%pip install transformers pytest accelerate safetensors trl peft datasets
!python modulo-a8/lab/lab_a8.py
!python -m pytest modulo-a8/testes -q
```

Saída: `modulo-a8/saidas/ca8.json` (gitignore; você entrega o seu). Cópia da autoria: [`execucao/ca8-autoria.json`](./execucao/ca8-autoria.json).

## O que o lab prova

- **A8.1.** Pares originais com **split treino/eval** (prompts disjuntos); rejected mais longo; `tokenize(prompt)` prefixo de prompt+compleção; perdas de caderno; APIs estável vs `experimental`.
- **A8.2.** DPO LoRA 8 passos (`trl.DPOTrainer` estável) no treino; `eval_rewards/accuracies` no **hold-out**. `aviso_prefixo_trl.ocorreu=false`. Compara logps vs o base congelado.
- **A8.3.** Cinco perdas **no mesmo lote do eval** + `dpo_vs_beta`; `nao_e_ranking=true` (unidades diferentes).
- **A8.4.** KTO e IPO na API estável (poucos passos); ORPO e SimPO em `trl.experimental` (1 passo) ou `falhou` documentado.
- **A8.5.** `nao_calibrado` (esta CPU não tem CUDA; harness/IC são alvo de T4).

Leitura extra opcional (Apache-2.0, **não** vendored): alinhamento em [lucianoon/llm-course](https://github.com/lucianoon/llm-course). O texto da aula continua nosso.
