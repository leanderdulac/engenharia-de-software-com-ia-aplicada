# Referências primárias — A9

Conferidas na API do arXiv / card Hugging Face em 12/11/2026. Texto da aula original.

## Papers

| Paper | Primeiro autor | Ano | arXiv | O que o A9 usa |
| --- | --- | --- | --- | --- |
| *Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning* | Williams | 1992 | — (ML journal; REINFORCE) | `∇ log π · (G − b)` |
| *High-Dimensional Continuous Control Using Generalized Advantage Estimation* | Schulman | 2015 | [1506.02438](https://arxiv.org/abs/1506.02438) | vantagem / GAE (PPO) |
| *Proximal Policy Optimization Algorithms* | Schulman | 2017 | [1707.06347](https://arxiv.org/abs/1707.06347) | clip `1±ε`, razão de importância |
| *Deep Reinforcement Learning from Human Preferences* | Christiano | 2017 | [1706.03741](https://arxiv.org/abs/1706.03741) | RLHF; contraste com verificável |
| *Defining and Characterizing Reward Hacking* | Skalse | 2022 | [2209.13085](https://arxiv.org/abs/2209.13085) | otimizar a regra ≠ a intenção |
| *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models* | Shao | 2024 | [2402.03300](https://arxiv.org/abs/2402.03300) | GRPO; `Â_i = (r_i − mean)/std` no grupo |
| *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning* | DeepSeek-AI | 2025 | [2501.12948](https://arxiv.org/abs/2501.12948) | GRPO em escala; `β` KL pequeno |

Williams 1992 não está no arXiv; a aula usa só a regra do gradiente.

## Modelos

| Id | Licença (card, nov/2026) | Notas |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | GRPO + LoRA; **não** é SFT Amplitude |

## Software

- `trl` 1.17.1: `GRPOTrainer` / `GRPOConfig` **estáveis**. `beta` **default 0.0** (sem modelo de referência).
- `peft` 0.21.2, `datasets` 5.2.0, `transformers` 5.22.2, `torch` 2.15.0+cpu.

## Tronco (citação, sem cópia)

- M09 `grpo_verifiable_reward_demo.py`: vantagem de grupo **sem** `optimizer.step`. Este A9 chama `train()`.
- A8: DPO off-policy; `beta` lá não é o KL do GRPO.
