# A5 — SFT sério

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca5.md`](./checkpoint-ca5.md). Sem gabarito nesta aula.

O collator do M09 mistura prompt e resposta. O A4 já mascarou −100. Aqui isso treina: LoRA no SmolLM2-135M, loss **só no assistant**, um π_SFT gravado, e A8/A9/A10 *podem* partir dele. Ao final:

1. contrastar assistant-only vs prompt+resposta no JSON;
2. ler acurácia no hold-out Amplitude (dois diálogos) — sem copiar o harness do M09;
3. olhar probes gerais (esquecimento) sem GSM8K/Dolly;
4. saber onde está o adapter e como A8 o desliga (`TRILHA_PI_SFT=0`).

Nada disto entra nas 240 h. Números saem do seu `ca5.json`.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| 3 sementes no harness Amplitude | 1 semente, n_eval=2; harness/IC `nao_calibrado` |
| GSM8K / Dolly | `nao_baixado`; probes `2+2=` e `The capital of France is` |
| W&B | não usado; histórico no JSON |
| T4 | `nao_calibrado` |

π_SFT vive em [`execucao/pi_sft/`](./execucao/pi_sft/). A8/A9/A10 chamam `carregar_base_ou_sft()`.

---

## 1. Assistant-only

A CE do HF já faz o shift do A3 e ignora −100. Se o prompt entrar na loss, o modelo copia o enunciado. O lab treina 64 passos LoRA (`q_proj`/`v_proj`, r=8) nos 4 diálogos do A4. Uma corrida curta **sem** máscara (8 passos) existe só para contraste — não é o π_SFT.

---

## 2. Esquecimento

SFT estreito empurra massa para JSON de sinistro. `2+2=` e uma frase em inglês são o canário. Queda **não** é medida com IC: n=2 probes, 1 semente. Se o JSON ainda imprime `4`, o canário viveu; se virar placa de carro, o domínio comeu a aritmética.

---

## 3. Tracking

Sem W&B. `a5_1.historico_tail`, `loss_ini`/`loss_fim`, `fracao_treino` (~LoRA). Três sementes no harness = T4.

---

## 4. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| loss assistant-only 64 passos | **1,34 → 0,046** |
| LoRA | 460 800 / 134 975 808 params (**0,34%**) |
| acc treino / eval | **1,00 / 0,50** (eval: Eva ok; Fabio mistura placa no nome) |
| probes `2+2=` | base `10.` → depois `4` (não piorou) |
| prompt+resposta 8 passos | loss 3,34 → 3,44; eval acc 0 |
| adapter | `execucao/pi_sft/` (~1,8 MB, sem tokenizer) |

---

## 5. O que fazer agora

1. `python modulo-a5/lab/lab_a5.py`
2. CA5 com o JSON **seu**.
3. A8/A9/A10: rode com o adapter no disco, ou `TRILHA_PI_SFT=0`.
