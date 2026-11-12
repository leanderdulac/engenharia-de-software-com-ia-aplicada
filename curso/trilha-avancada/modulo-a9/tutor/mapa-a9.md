# Mapa de subhabilidades — A9 (RL até GRPO)

**Tema:** REINFORCE, PPO, GRPO, recompensa verificável  
**Fontes:** `modulo-a9/aula.md`, `lab/`, `checkpoint-ca9.md`. M09 GRPO demo citado, não copiado. A8 citado (DPO off-policy). Licença pendente.

**Como usar:** cole `tutor/tutor-socratico-ptbr.md` **e** este mapa. Níveis 0–5 do tutor **não** substituem CA9. Não revelar gabarito nem inventar recompensa.

A7 não foi publicado. T4 não calibrada.

## Prompt de início

```
Use o tutor socrático com este mapa do A9 (RL verificável / GRPO).
Método socrático, uma pergunta por vez, níveis 0–5.
Não entregue gabarito nem invente recompensa de lab; peça o ca9.json.
A7/A5 ausentes: GRPO no SmolLM2 base; o demo do M09 não atualiza pesos.
Comece pelo diagnóstico e mostre o mapa inicial.
```

## Subhabilidades

### A. Peças do MDP no LLM

- **Domínio 4/5:** mapear prompt/token/compleção/r final para s, a, π, τ, r.
- **Perguntas:** 1) Onde está o estado a meio da geração? 2) A recompensa da soma chega em que token? 3) DPO amostra π no laço?
- **Limite:** “trajetória = o dataset JSONL”.
- **Fonte:** aula §1. **CA9** parágrafo.

### B. REINFORCE e baseline

- **Domínio 4/5:** `∇ log π · (G − b)`; b não viciado se independe de a.
- **Perguntas:** 1) G=0, o que o gradiente faz na ação amostrada? 2) Neste bandit o baseline *precisa* subir p*? 3) 4 ações, p uniforme inicial?
- **Fonte:** aula §2; `reinforce.py`. **CA9.1**.

### C. PPO vs GRPO

- **Domínio 4/5:** clip ρ; GRPO Â no grupo; sem crítico; G≥2; se std=0 o sinal some.
- **Perguntas:** 1) Por que G=1 é ilegal no TRL? 2) `frac_reward_zero_std≈0,21` depois de G=4 implica o quê? 3) `beta` default no TRL 1.17?
- **Limite:** colar DeepSeek-R1 0,001 como se fosse o default do lab.
- **Fonte:** aula §§3–4; Shao 2402.03300. **CA9.3**.

### D. Verificável e hacking

- **Domínio 4/5:** primeiro inteiro vs formato vs dígito qualquer; `"0"` e `"70"` ganham no hack.
- **Perguntas:** 1) `"10\n\nA."` com ouro 8: qual recompensa em cada regra? 2) Por que hack_media=1 no base não é “o modelo sabe somar”? 3) Por que o prompt não pode terminar em `=\n`?
- **Fonte:** aula §5; `hacking.py`. **CA9.2**, **CA9.4**.

### E. Medição honesta / T4

- **Domínio 4/5:** n_eval=80, 3 seeds, média±desvio; 1 flip em n=4 era ruído; n=3 não é IC 95%.
- **Perguntas:** 1) delta 0,133 ± 0,007: o que o desvio entre seeds diz? 2) `melhorou_claro` vs IC? 3) KL 0,016 com eval igual ao β=0 — o que reportar?
- **Fonte:** aula §§6–7. **CA9.3**, **CA9.5**.

O tutor não revela `gabarito-instrutor/` nem amostras da autoria como se fossem do aluno.
