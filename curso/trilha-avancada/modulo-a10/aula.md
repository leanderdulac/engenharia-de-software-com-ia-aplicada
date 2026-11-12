# A10 — Destilação

Trilha avançada, **opcional**. Guia da pasta: [`README.md`](./README.md). Checkpoint: [`checkpoint-ca10.md`](./checkpoint-ca10.md). Esta aula **não** contém gabarito de CA10.

No A9 o aluno *melhorou a si mesmo* com recompensa verificável. Aqui alguém maior ensina: professor, aluno, respostas sintéticas, filtro, CE na sequência, KL nos logits. Ao final você deve conseguir:

1. distinguir destilação por resposta, por logits (temperatura + KL) e por features;
2. dizer por que logits exigem o **mesmo tokenizer**;
3. montar um pipeline sintético com verificador (não copiar lixo do professor);
4. situar self-distillation e reasoning distillation sem fingir que rodou CoT (A7 esqueleto);
5. ler uma tabela professor × aluno original × aluno destilado em qualidade, latência e memória;
6. checar a **licença** do professor antes de treinar o aluno.

Nada disto entra nas 240 h. Números do SmolLM2 **não** se copiam da aula: saem do seu `ca10.json`.

---

## 0. Honestidade de dependências

A5 (SFT) e A7 (raciocínio) são esqueleto. Consequências:

| O plano original pedia | O que este módulo faz |
| --- | --- |
| Aluno = SFT da trilha | SmolLM2-135M **base** + LoRA |
| Professor API / 7B | SmolLM2-360M (Apache-2.0, mesmo tokenizer) |
| Traces CoT (reasoning KD) | aula; lab não gera cadeia longa |
| T4, custo/1k, IC | `nao_calibrado` |

Qwen2.5-0.5B também é Apache-2.0 (card, nov/2026) mas o vocabulário **não** é o do aluno — logits KD quebraria. O lab não o baixa.

---

## 1. Professor e aluno

O professor `π_T` é maior (ou só melhor na tarefa). O aluno `π_S` é o que você vai servir. Destilar é treinar `π_S` para parecer `π_T` **sem** carregar `π_T` na inferência.

Custo típico: treino usa os dois; serving usa só o aluno. Nesta CPU o professor 360M tem pegada **1447 MB** e p50 **0,146 s**/prompt; o aluno 135M **538 MB** e **0,045 s**. Qualidade na soma curta: professor **0,917** (55/60), aluno original **0,600** (36/60).

---

## 2. Três famílias

### Por resposta / sequência (Kim & Rush 2016, [1606.07947](https://arxiv.org/abs/1606.07947))

O professor gera `y_T ~ π_T(·|x)` (greedy aqui). O aluno faz SFT em `(x, y_T)`: `−log π_S(y_T | x)` só nos tokens da compleção. Caixa-preta: basta texto. O lab filtra `y_T` com o verificador *antes*.

### Por logits, com temperatura (Hinton et al. 2015, [1503.02531](https://arxiv.org/abs/1503.02531))

```text
p_T(a|s) = softmax( z_T / T )
p_S(a|s) = softmax( z_S / T )
L = T²  KL( p_T  ||  p_S )
```

`T>1` amacia a distribuição (as classes “quase certas” ainda ensinam). `T²` mantém a escala do gradiente. Exige **os mesmos ids** — daí o mesmo tokenizer SmolLM2.

### Por features

Uma camada do professor (hint, Romero et al.) casa com uma do aluno. Útil quando os vocabulários diferem. O lab **não** implementa.

Self-distillation: professor = aluno (ou checkpoint anterior). Reasoning distillation: o professor solta CoT e o aluno imita o *rastro*, não só a resposta. A7 ausente: fica na aula.

---

## 3. Dados sintéticos e o filtro

Gerar não é o fim. O professor também erra. Pipeline desta aula:

1. prompts de treino (32 somas, programáticas);
2. professor greedy 8 tokens;
3. verificador: primeiro inteiro == ouro;
4. só os aceitos entram no aluno.

Nesta VM: **32/32 aceitos** (taxa 1,0). Isso é a tarefa fácil, não um milagre. No hold-out o professor ainda erra 5/60. Sem filtro, você destilararia `"10"` como se fosse `6`.

Licença do sintético: herda a do professor. Apache-2.0 **permite** treinar o aluno. Termos de API comercial muitas vezes **proíbem**. O JSON traz o manifesto.

---

## 4. Combinar com SFT / LoRA

SFT no ouro humano e destilação no sintético do professor são a mesma perda CE — muda o *rótulo*. LoRA no aluno (`q_proj`/`v_proj`, r=8) é o que cabe nesta CPU. Merge/GGUF é A6 (esqueleto).

Retenção / esquecimento: treinar só em somas pode estragar prosa. O lab **não** mede perplexidade geral (`esquecimento: nao_medido`). Quem forçar “não esqueceu” sem número zera.

---

## 5. O que o lab mediu (hold-out n=60)

| Modelo | acc | n_acertos | p50 (s) | pegada (MB) |
| --- | ---: | ---: | ---: | ---: |
| professor 360M | **0,917** | 55 | 0,146 | 1447 |
| aluno original 135M | 0,600 | 36 | 0,045 | 538 |
| aluno sequência (8 passos) | **0,650** | 39 | 0,052 | 540 |
| aluno logits T=2 (8 passos) | **0,383** | 23 | 0,045 | 540 |

Sequência **subiu** 5 p.p. Logits **caiu**. Oito passos de KL no vocabulário inteiro, LoRA r=8, CPU, não é DistilBERT. A aula não transforma isso em “logits é pior para sempre”: é o que *esta* receita mediu. T=4 (2 passos) só acende a curva (`loss≈1,87` → `1,83`); não compete com T=2 de 8 passos.

Qualidade × latência × memória: o professor ganha acerto e perde os três outros eixos. O aluno destilado por resposta fica no meio da acurácia, perto do aluno original em p50/pegada.

---

## 6. O que fazer agora

1. Ler Hinton §2 (temperatura) e esta §2.
2. `python modulo-a10/lab/lab_a10.py`
3. CA10 com o JSON **seu**. Se logits piorar, o parágrafo cita o número.
4. Opcional: [`tutor/mapa-a10.md`](./tutor/mapa-a10.md).

T4: não troque o `torch` CUDA. Não copie 0,917 desta CPU.
