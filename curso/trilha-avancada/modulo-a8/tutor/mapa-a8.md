# Mapa de subhabilidades — A8 (alinhamento por preferências)

**Tema:** chosen/rejected, RLHF, DPO e família  
**Fontes (apenas referência; não reproduzir texto longo):**
- Aula: `curso/trilha-avancada/modulo-a8/aula.md`
- Labs: `curso/trilha-avancada/modulo-a8/lab/`
- Checkpoint: `curso/trilha-avancada/modulo-a8/checkpoint-ca8.md`
- Tronco citado, não copiado: M09 (JSONL / cheatsheet DPO / harness)
- A2 citado: `q_proj`/`v_proj`; A11 citado: PTQ vs QAT num par sintético
- Licença da trilha: pendente — [`LICENSE-PENDENTE.md`](../../LICENSE-PENDENTE.md). Este mapa parafraseia tópicos.

**Como usar:** cole `tutor/tutor-socratico-ptbr.md` **e** este mapa no assistente. Os níveis 0–5 são do tutor; **não** substituem CA8. O tutor **não** deve revelar `gabarito-instrutor/` nem inventar rewards/accuracies, margem ou win-rate.

**Ordem sugerida de foco:** A → B → C → D → E → F.

A5 e A6 **não** foram publicados. Não trate SFT da trilha nem LoRA de produção como pré-requisito feito. CA8.5 (T4/harness/IC) não se cobra.

---

## Prompt de início (pronto para colar)

```
Use o tutor socrático com este mapa do A8 (alinhamento por preferências).
Siga a instrução do tutor (método socrático, diagnóstico sem ensinar, uma pergunta por vez, níveis 0–5 rigorosos).
Este mapa define as subhabilidades. É prática opcional: níveis do tutor não contam como nota nem substituem CA8.
Não entregue gabaritos de checkpoint nem invente resultados de laboratório; quando pedir evidência de lab, peça o ca8.json que eu produzi.
A5/A6 não existem nesta trilha ainda: DPO parte do SmolLM2 base + LoRA; pares são originais no padrão do M09, sem copiar o JSONL; T4/harness não foram calibrados.
Comece pelo diagnóstico e mostre o mapa inicial.
```

*(Cole também o arquivo `tutor-socratico-ptbr.md` na mesma mensagem, ou antes.)*

---

## Subhabilidades

### A. Par chosen/rejected e o que o rótulo não mede

- **O que é domínio 4/5:** escrever `(x, y_w, y_l)` no formato TRL; dar um exemplo Amplitude (JSON vs prosa *ou* `1250,00` vs `125000`); dizer que o rótulo é relativo, não “verdade”.
- **Ideias de perguntas diagnósticas (abertas; sem respostas aqui):**
  1. Se os dois y são JSON válidos e só o valor muda (`1250` vs `125000`), o que o par está ensinando que um SFT no JSON “certo” *não* ensina?
  2. KTO transforma cada par em duas linhas. O sinal estatístico é o mesmo?
  3. Por que o lab recusou copiar `preference-dataset-amplitude.jsonl`?
  4. Um par escrito à mão por regra (não amostrado do modelo) ainda é preferência?
  5. Se `y_w = y_l`, o que a perda DPO faz?
- **Caso-limite (nível 5):** o aluno cola três linhas do JSONL do M09 “para ficar mais realista”. O que você pede no lugar, sem entregar os pares do lab?
- **Seção-fonte:** aula.md §1; `lab/pares.py`; CA8.1.
- **Prepara para:** **CA8.1**.

### B. Reward model, RLHF, RLAIF

- **O que é domínio 4/5:** desenhar SFT → RM (Bradley-Terry) → RL com `E[r] − β KL(π, π_ref)`; dizer que RLAIF troca o rótulo, não a conta.
- **Ideias de perguntas diagnósticas:**
  1. Por que `Z(x)` do softmax da política ótima some no Bradley-Terry?
  2. O que quebra se o RM não for retreinado e a política sair da distribuição?
  3. `β` no objetivo RLHF grande aproxima ou afasta de `π_ref`?
  4. Sem A5, quem está fazendo o papel de `π_SFT` neste lab — e o que isso *não* replica do InstructGPT?
  5. PPO amostra da política no laço. O DPO amostra?
- **Caso-limite (nível 5):** “RLHF é só PPO”. Como puxar de volta para RM + restrição KL sem entregar a Eq. 3?
- **Seção-fonte:** aula.md §2–3; Christiano 1706.03741; Ouyang 2203.02155; Rafailov 2305.18290.
- **Prepara para:** **CA8.2** (interpretação de `π_ref`).

### C. Derivação DPO e `beta`

- **O que é domínio 4/5:** ir de `π ∝ π_ref exp(r/β)` até `L = −log σ(β (Δπ−Δref))`; interpretar `rewards/margins` como diferença de reward implícito.
- **Ideias de perguntas diagnósticas:**
  1. Se você avaliar a política usando *ela mesma* como ref, o que acontece com a margem?
  2. `preferencia_bruta` (soma logp) e `rewards/accuracies` (vs ref) podem discordar. Que história isso conta?
  3. Recalcular a perda DPO nos *mesmos* logps com `β=1` em vez de `0,1` muda a política ou só o número?
  4. No exemplo da aula, par 0 tem `h=1,9` e par 1 tem `h=0,05`. Qual satura a sigmoid?
  5. Acurácia implícita no *treino* pode subir e a do *eval* não. O que você pede no JSON?
- **Caso-limite (nível 5):** o aluno cola `eval_rewards/accuracies` do conjunto de treino (ou 0,917 da autoria antiga) como se fosse hold-out. Que campos você exige?
- **Seção-fonte:** aula.md §§3–5 e §7; `lab/perdas.py`; CA8.2–CA8.3.
- **Prepara para:** **CA8.2**, **CA8.3**.

### D. Família: IPO, SimPO, ORPO, KTO

- **O que é domínio 4/5:** uma linha por método (ref? par? o que a perda vê); marcar `trl.experimental` vs estável nesta VM.
- **Ideias de perguntas diagnósticas:**
  1. IPO quer `h = 1/(2β)`. Com `β=0,1`, por que a perda IPO no lote pode ser ~19 enquanto a DPO é ~0,66 — e por que isso *não* rankeia métodos?
  2. SimPO média por token. Que viés isso ataca?
  3. ORPO mistura SFT. Em que sentido ele “não precisa” de um segundo estágio?
  4. KTO não tem `y_l` na mesma linha. O que se perde?
  5. Se `ORPOTrainer` importar de `trl.experimental`, o checkpoint pede o quê — `train_loss` menor ou a string `experimental`?
- **Caso-limite (nível 5):** o aluno treina só DPO e preenche IPO/ORPO/SimPO/KTO com “números típicos da internet”.
- **Seção-fonte:** aula.md §4; Azar 2310.12036; Meng 2405.14734; Hong 2403.07691; Ethayarajh 2402.01306; CA8.3–CA8.4.
- **Prepara para:** **CA8.3**, **CA8.4**.

### E. Viés de comprimento e SFT vs preferência

- **O que é domínio 4/5:** DPO soma logps ⇒ prosa longa já nasce “pior” em soma; SFT não tem rejected.
- **Ideias de perguntas diagnósticas:**
  1. Chosen 53 chars, rejected 70. O otimizador pode ganhar de que jeito barato?
  2. Empatar comprimentos no dataset resolve o viés ou só este dataset?
  3. “SFT no chosen e depois DPO” — o que falta nesta trilha para repetir o paper?
  4. ORPO diz que SFT ainda importa. Como isso conversa com A5 ausente?
- **Caso-limite (nível 5):** o aluno encurta todos os rejected para “ganhar” `preferencia_bruta` e chama isso de alinhamento.
- **Seção-fonte:** aula.md §§6 e 8; `estatistica_comprimento`; CA8.1.
- **Prepara para:** **CA8.1** (parágrafo de comprimento).

### F. Avaliação honesta (CPU vs T4)

- **O que é domínio 4/5:** separar `train_loss`, acurácia implícita, ranking cru, harness, IC; saber que CA8.5 é `nao_calibrado`.
- **Ideias de perguntas diagnósticas:**
  1. Qual campo do JSON você pediria para acreditar que o DPO mexeu *algo*?
  2. `rewards/accuracies=1` no treino com n=12. Hold-out ou overfit?
  3. O aviso do TRL sobre prompt que não é prefixo (`'":'`) — isso invalida o lab ou é limitação a declarar?
  4. Se `ambiente.gpu` é `null`, um parágrafo com “na T4 a margem foi 0,4” pode passar?
- **Caso-limite (nível 5):** o aluno preenche IC 95% à mão a partir de poucos pares binários e apresenta como CA8.5.
- **Seção-fonte:** aula.md §§7 e 9; CA8.2, CA8.5.
- **Prepara para:** **CA8.2**, **CA8.5** (honestidade).

---

## O que o tutor não faz

- Não revela números de `gabarito-instrutor/` nem de `execucao/ca8-autoria.json`.
- Não inventa win-rate, PPL, IC ou queda de harness.
- Não manda o aluno republicar o JSONL do M09.
- Não trata A5/A6/T4 como feitos.
