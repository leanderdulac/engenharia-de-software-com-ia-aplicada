# A7 — Raciocínio treinável

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca7.md`](./checkpoint-ca7.md). Sem gabarito nesta aula.

O M04 ensina ReAct como **agente**. Aqui o raciocínio é **texto que se treina**: CoT vs resposta direta, voto (self-consistency), verificador de resultado vs de passo. Em 135M o CoT **pode piorar** — isso vale. Ao final:

1. contrastar acc direto vs CoT no JSON;
2. aplicar voto em n amostras;
3. marcar “certo pelo motivo errado”;
4. não fingir GSM8K nem IC 95%.

Nada disto entra nas 240 h.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| GSM8K | `nao_baixado`; 8 somas originais |
| IC 95% | `nao_calibrado` |
| T4 / 0,5B instruct | SmolLM2-135M **base** (π_SFT é JSON, não CoT) |
| M04 ReAct | apontado, **não copiado** |

---

## 1. CoT como dado

“Pense em voz alta… Resposta: N” é um *formato*, não magia. Se o modelo não sabe somar, a cadeia alucina e o parser ainda pode pescar um dígito. Verificador de **resultado** (primeiro inteiro) ≠ verificador de **passo** (as parcelas aparecem?).

Self-consistency: amostra T>0, vota o inteiro. Não é treino.

---

## 2. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| acc direto / CoT / SC | **0,375 / 0,375 / 0,250** (n=8) |
| cot_piorou | false (empatou; SC piorou) |
| certo_motivo_errado | **0,250** |
| exemplo 4+5 | direto `10`; CoT `11` |

---

## 3. O que fazer agora

1. `python modulo-a7/lab/lab_a7.py`
2. CA7 com o JSON **seu**.
3. A9 já usa o verificador de resultado como recompensa.
