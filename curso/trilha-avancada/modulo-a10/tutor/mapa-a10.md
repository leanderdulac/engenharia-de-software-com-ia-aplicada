# Mapa de subhabilidades — A10 (destilação)

**Tema:** professor/aluno, sequência vs logits, filtro, licença  
**Fontes:** `modulo-a10/aula.md`, `lab/`, `checkpoint-ca10.md`. A5/A7 esqueleto. Licença pendente da trilha.

## Prompt de início

```
Use o tutor socrático com este mapa do A10 (destilação).
Método socrático, uma pergunta por vez, níveis 0–5.
Não entregue gabarito nem invente acurácia; peça o ca10.json.
Comece pelo diagnóstico e mostre o mapa inicial.
```

## Subhabilidades

### A. Professor vs aluno

- **Domínio 4/5:** quem gera o rótulo; quem serve.
- **Perguntas:** 1) Por que o professor 1447 MB não vai para produção desta receita? 2) Acc 0,92 vs 0,60: o que ainda falta medir?
- **Fonte:** aula §1. **CA10.1–2**.

### B. Sequência vs logits vs features

- **Domínio 4/5:** CE em y_T; KL com T; hint layers; mesmo tokenizer.
- **Perguntas:** 1) Qwen2.5-0.5B Apache e mesmo assim fora do lab de logits — por quê? 2) O que T faz na softmax?
- **Fonte:** aula §2; Hinton 1503.02531. **CA10.3–4**.

### C. Filtro e licença

- **Domínio 4/5:** verificador; sintético herda o termo do professor; API comercial ≠ Apache.
- **Perguntas:** 1) Taxa de aceite 1,0 no treino e 5 erros no eval: o filtro é inútil? 2) Pode treinar aluno em completions de um chat comercial?
- **Fonte:** aula §3. **CA10.1**.

### D. Tabela honesta

- **Domínio 4/5:** qualidade × p50 × pegada; 8 passos de KL podem piorar; máscara/shift/T² certos não salvam a receita.
- **Perguntas:** 1) Sequência 0,65, logits 0,38, mista 0,57: qual frase o parágrafo deve trazer? 2) Se `shift_alinhado=true`, a queda ainda pode ser “bug de shift”? 3) T4 `nao_calibrado`?
- **Fonte:** aula §5 e §5.1. **CA10.4–6**.

O tutor não revela `gabarito-instrutor/`.
