# A12 — Projeto final da trilha

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca12.md`](./checkpoint-ca12.md). Sem gabarito nesta aula.

Não é um capstone do zero. O C09.5 já pediu um ADR Amplitude. Aqui você **reabre** essa decisão com duas técnicas da trilha, medidas **neste** hardware, e escreve um ADR **novo** ([`adr-capstone.md`](./adr-capstone.md)) — sem copiar o do M09. Ao final:

1. apontar no JSON as duas técnicas e os números;
2. decidir, com evidência, se π_SFT ajuda a preferência JSON e se INT8 cabe no ppl;
3. recusar o que não compensou, com número;
4. não misturar T4 imaginário.

Nada disto entra nas 240 h. Não substitui C09.5.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| Dois treinos pesados (DPO + GRPO) | **não**. A8 entra como logps; A11 como PTQ |
| Harness M09 / IC 95% | `nao_calibrado` |
| T4 | `nao_calibrado` |
| ADR do tronco | apontado, **não copiado** |

---

## 1. Duas técnicas

*Preferência implícita* (A8): `log P(chosen) > log P(rejected)` no hold-out, base vs π_SFT. Sem `DPOTrainer`.

*PTQ INT8* (A11): ppl no corpus curto, lm_head em fp32. Mesma âncora do A11.

Se INT8 piorar o ppl e o SFT não subir a preferência, o ADR **recusa** promoção — a regra do M09.

---

## 2. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui.

| Item | Medido |
| --- | --- |
| preferencia_bruta base / π_SFT | **0,50 → 1,00** (n=4) |
| ppl fp32 / int8 | **217 → 950** (INT8 piorou) |
| ADR | π_SFT sim; INT8 **não** promover |

---

## 3. O que fazer agora

1. `python modulo-a12/lab/lab_a12.py`
2. Completar [`adr-capstone.md`](./adr-capstone.md) com os campos do **seu** JSON.
3. CA12.
