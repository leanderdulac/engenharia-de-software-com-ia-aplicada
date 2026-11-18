# A9 — RL com recompensa verificável

**Status:** esqueleto (não publicado). **Carga prevista:** 8 h. **Pré-requisito previsto:** A7, A8.

A8 está **publicado** (DPO no SmolLM2 base + LoRA; T4/harness não calibrados). A7 ainda é esqueleto: a aula A9 terá de ser honesta sobre raciocínio treinável e sobre o demo GRPO do M09 que **não** atualiza pesos.

O demo `grpo_verifiable_reward_demo.py` do M09 calcula vantagem de grupo **sem atualizar pesos**. Este módulo: REINFORCE de brinquedo em CPU; `GRPOTrainer` de verdade (TRL) com LoRA; reward hacking proposital; tabela SFT × DPO × GRPO. Atenção: no TRL atual o `beta` (KL) padrão é **0.0**.

**CA9:** curva com/sem baseline; recompensa de treino sobe **e** o retido melhora com IC (ou o relatório mostra por que não); exemplos do hack; ADR da comparação.
