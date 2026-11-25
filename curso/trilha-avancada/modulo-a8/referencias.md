# Referências primárias — A8

Conferidas na API do arXiv / card Hugging Face em 12/11/2026. Citação acadêmica; o texto da aula é original.

## Papers

| Paper | Primeiro autor | Ano | arXiv | O que o A8 usa |
| --- | --- | --- | --- | --- |
| *Deep Reinforcement Learning from Human Preferences* | Christiano | 2017 | [1706.03741](https://arxiv.org/abs/1706.03741) | RLHF: preferência → reward → política |
| *Proximal Policy Optimization Algorithms* | Schulman | 2017 | [1707.06347](https://arxiv.org/abs/1707.06347) | PPO no estágio RL da pipeline clássica |
| *Fine-Tuning Language Models from Human Preferences* | Ziegler | 2019 | [1909.08593](https://arxiv.org/abs/1909.08593) | LM + RLHF; `π_ref` / KL |
| *Training language models to follow instructions with human feedback* | Ouyang | 2022 | [2203.02155](https://arxiv.org/abs/2203.02155) | InstructGPT: SFT → RM → PPO |
| *Constitutional AI: Harmlessness from AI Feedback* | Bai | 2022 | [2212.08073](https://arxiv.org/abs/2212.08073) | RLAIF / juiz-modelo |
| *RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback* | Lee | 2023 | [2309.00267](https://arxiv.org/abs/2309.00267) | AI feedback no lugar do humano |
| *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* | Rafailov | 2023 | [2305.18290](https://arxiv.org/abs/2305.18290) | `π* ∝ π_ref exp(r/β)`; `L = −log σ(β (Δπ−Δref))`; Z cancela |
| *A General Theoretical Paradigm to Understand Learning from Human Preferences* | Azar | 2023 | [2310.12036](https://arxiv.org/abs/2310.12036) | ΨPO; IPO = Identidade; `(h − 1/(2β))²` |
| *KTO: Model Alignment as Prospect Theoretic Optimization* | Ethayarajh | 2024 | [2402.01306](https://arxiv.org/abs/2402.01306) | alinhamento *unpaired*; HALO / prospect theory |
| *ORPO: Monolithic Preference Optimization without Reference Model* | Hong | 2024 | [2403.07691](https://arxiv.org/abs/2403.07691) | SFT + odds-ratio; sem `π_ref` |
| *SimPO: Simple Preference Optimization with a Reference-Free Reward* | Meng | 2024 | [2405.14734](https://arxiv.org/abs/2405.14734) | média por token, margem γ, sem ref |

Bradley-Terry (1952), *Rank Analysis of Incomplete Block Designs*, não está no arXiv; a aula usa só `P = σ(r_w − r_l)`.

## Modelos (lab)

| Id | Licença (card, nov/2026) | Notas |
| --- | --- | --- |
| [`HuggingFaceTB/SmolLM2-135M`](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Apache-2.0 | base + LoRA; o mesmo do A2/A11. **Não** é um SFT Amplitude |

## Software

- Hugging Face `trl` 1.17.1 (autoria): `DPOTrainer` / `KTOTrainer` estáveis; `ORPOTrainer` e `CPOTrainer` (SimPO) em `trl.experimental`.
- `peft` 0.21.2 (LoRA r=8, `q_proj`/`v_proj`).
- `datasets` 5.2.0.
- `transformers` 5.22.2, `torch` 2.15.0+cpu.

APIs mudam de minor. Se `trl.experimental.orpo` sumir, o JSON deve trazer `status=falhou` com o erro — não invente `train_loss`.

## Tronco (citação, sem cópia)

- M09: cheatsheet DPO, JSONL de pares Amplitude, LoRA `q_proj`/`v_proj`, harness do decimal — **não** republicamos o JSONL.
- M01: temperature / amostragem (o DPO mexe nos *logits treináveis*, não no sampler).
- A2: bloco, GQA, `q_proj`/`v_proj`.
- A11: PTQ; um dos pares sintéticos pergunta PTQ vs QAT.
