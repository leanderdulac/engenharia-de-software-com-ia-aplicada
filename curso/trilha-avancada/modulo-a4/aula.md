# A4 — Dados para SFT no nível do token

Trilha avançada, **opcional**. [`README.md`](./README.md). Checkpoint: [`checkpoint-ca4.md`](./checkpoint-ca4.md). Sem gabarito nesta aula.

O M09 já limpa JSONL e faz split por entidade. Aqui o JSONL vira tensor: template de chat, system como *dado*, labels −100 no prefixo, EOS, padding. Ao final:

1. dizer o que o tokenizer base *não* traz de chat template, e o que o lab declara;
2. apontar, no JSON, que o prefixo está em −100 e o assistant termina em EOS;
3. medir o custo em tokens de ligar o system (acurácia fica para o A5);
4. truncar um lote e ver o assistant encolher.

Nada disto entra nas 240 h. Números saem do seu `ca4.json`.

---

## 0. Honestidade

| Plano | Nesta CPU |
| --- | --- |
| JSONL Amplitude da turma | diálogos **originais** no espírito Amplitude; o JSONL do M09 **não** é lido |
| oasst1 | `nao_baixado` |
| instruct ~0,5B | SmolLM2-135M **base** (já no cache); Instruct não baixado |
| T4 | `nao_calibrado` |

O base **não** traz `chat_template`. O lab usa `### system / ### user / ### assistant` em ASCII, desta trilha — não o template do Instruct.

---

## 1. Por que −100

A CE do A3 é no *próximo* token. Se o prompt entrar na loss, o modelo gasta gradiente copiando o enunciado. Convenção do HF: `labels[i] = -100` ignora a posição. Máscara desta aula:

```text
labels = [-100] * n_prompt  +  ids_assistant
```

O prefixo inclui o cabeçalho `### assistant\n`. Só o JSON (e o EOS) treinam.

Tokenizar prefixo e assistant **separados** e concatenar evita fusão BPE na fronteira. Re-encodar a string inteira pode mudar `n_prompt`.

---

## 2. System é dado

Ligar o system aumenta `n_prompt` (~dezenas de tokens neste lab) e **não** muda `n_assistant`. Mais contexto, mesma loss-alvo. Se a acurácia no eval sobe ou desce, isso é A5 — aqui só cabe no orçamento.

Multi-turn: cada `user` é −100; cada `assistant` (sem o cabeçalho) entra na loss. Treinar o modelo a imitar a pergunta do usuário é o mesmo erro do prefixo.

---

## 3. EOS, pad, truncar

Sem EOS, a geração não sabe parar. Pad à direita: `input_ids` recebe `pad_id`, **labels** recebem −100, `attention_mask` recebe 0. Truncar à direita com `max_len` pequeno corta o assistant — o JSON mostra `n_assistant` caindo. Em produção corta-se o prefixo, não a resposta.

---

## 4. O que o lab mediu

Números da autoria (CPU). O seu JSON substitui esta tabela.

| Item | Medido |
| --- | --- |
| `chat_template` no tokenizer | **ausente** (base) |
| split treino/eval | disjunto |
| treino+sys | n_prompt 71,0 · n_asst 31,75 · 69% prompt |
| Δ `n_prompt` com system | **+33 tok** (n_assistant igual) |
| todos EOS | true (`<\|endoftext\|>`) |
| trunc 48 | L=48, **n_assistant 31,75 → 0** (corta só o prefixo; o JSON some) |

---

## 5. O que fazer agora

1. `python modulo-a4/lab/lab_a4.py`
2. CA4 com o JSON **seu**.
3. A5 usa estes tensores no SFT.
