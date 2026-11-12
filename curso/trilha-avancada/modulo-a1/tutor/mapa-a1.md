# Mapa de subhabilidades — A1 (tokens, logits e amostragem)

**Tema:** tokenização, softmax, temperature, top-k, top-p, laço  
**Fontes:** `modulo-a1/aula.md`, `lab/`, `checkpoint-ca1.md`. A0 esqueleto. Licença pendente da trilha.  
**Tronco citado, não copiado:** M01 seção “LLM: amostragem, não oráculo”; `exemplo-04`.

## Prompt de início

```
Use o tutor socrático com este mapa do A1 (tokens, logits e amostragem).
Método socrático, uma pergunta por vez, níveis 0–5.
Não entregue gabarito nem invente razão PT/EN; peça o ca1.json.
Comece pelo diagnóstico e mostre o mapa inicial.
```

## Subhabilidades

### A. Token e BPE

- **Domínio 4/5:** id inteiro; vocabulário fechado; BPE junta pares frequentes; `Segurado` não é 1 token neste lab.
- **Perguntas:** 1) O que o modelo vê: letra, palavra ou id? 2) Por que `|V|` finito ainda traduz palavra nova? 3) O `Ġ` é português?
- **Fonte:** aula §2; Sennrich 1508.07909. **CA1.1**.

### B. Custo PT vs EN

- **Domínio 4/5:** tokens/char; razão PT/EN do JSON; API cobra token; janela em tokens.
- **Perguntas:** 1) Se PT tem 21 e EN 15, o que muda no orçamento? 2) Caracteres dão razão ≈1 — o que isso mostra? 3) Estourar 8192 faz o quê?
- **Fonte:** aula §2. **CA1.1**.

### C. Softmax e temperatura

- **Domínio 4/5:** `softmax(z/T)`; T<1 afia; greedy = argmax, não T=0; entropia sobe com T.
- **Perguntas:** 1) O slider 0 do M01 divide por zero? 2) Se H(T=2) ≈ 9 nats e log\|V\|≈10,8, está uniforme? 3) Qual token ganha no top-5 do JSON?
- **Fonte:** aula §5; exemplo 04. **CA1.2**.

### D. Top-k, top-p, greedy

- **Domínio 4/5:** k fixo vs núcleo p; Holtzman; laço = `generate` greedy.
- **Perguntas:** 1) Top-p é o slider do M01? 2) Se Δ vs HF não é 0, o que você pede no JSON? 3) Por que greedy em 8 tokens ainda solta lixo depois do `4`?
- **Fonte:** aula §6; Holtzman 1904.09751. **CA1.2**.

### E. Treino × forward × geração

- **Domínio 4/5:** CE paralela com teacher forcing; um `forward` devolve todos os logits; geração é série.
- **Perguntas:** 1) No treino, o modelo vê o ouro na posição 3 mesmo se teria errado na 2? 2) Destilação do A10 usa qual dos três? 3) Onde entra KV cache (sem pedir o A11)?
- **Fonte:** aula §4. Prepara A3.

O tutor não revela `gabarito-instrutor/`.
