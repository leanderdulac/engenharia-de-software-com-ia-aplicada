# ADR — capstone da trilha (Amplitude)

Obra nova desta trilha. **Não** copia `decisoes-de-arquitetura.md` do M09. Parte do C09.5: o aluno já decidiu se treinar pesos na Amplitude. Aqui a decisão é *qual técnica da trilha entra no próximo round*, com números do `ca12.json`.

## Contexto

Caso Amplitude (JSON de sinistro). Hardware desta corrida: CPU, SmolLM2-135M. GPU T4 = `nao_calibrado`.

## Técnicas medidas neste lab

1. **A8 logps** (preferência implícita chosen/rejected, sem retreinar DPO)
2. **A11 PTQ INT8** (servir mais barato)

## Decisão 1 — SFT / π_SFT como política

- Evidência (autoria): `preferencia_bruta` 0,50 (base) → **1,00** (π_SFT), n=4 hold-out A8.
- Decisão: **manter π_SFT** como ponto de partida para o JSON Amplitude nesta CPU. n=4 não é IC; T4/`nao_calibrado`.

## Decisão 2 — PTQ para servir

- Evidência (autoria): ppl 217 → **950** no INT8 dinâmico (lm_head fp32).
- Decisão: **não promover INT8** neste 135M / corpus. O A11 já mostrou o lm_head; aqui o ppl explode mesmo protegendo. Servir em fp32 (ou esperar T4).

## Alternativa rejeitada

DPO/GRPO/destilação **retreinados** neste capstone. Custo CPU vs evidência já existente nos módulos. Números históricos de A8–A10 **não** se misturam com estes.

## Consequências

T4 / harness M09 / IC 95% continuam `nao_calibrado`. Promover a produção sem esses números é a mesma recusa do M09.

## Ligação ao C09.5

O ADR do tronco continua a ser o entregável de C09.5. Este arquivo **não** o substitui.
