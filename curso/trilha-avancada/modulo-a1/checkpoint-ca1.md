# CA1 — checkpoint objetivo (aluno)

Prática **opcional**. Não substitui C01–C09. Gabarito do instrutor **não** entra na entrega.

Entregue `saidas/ca1.json` gerado na **sua** máquina e um parágrafo (máx. 1 página).

## CA1.1 — tokenização PT vs EN

| Critério | Campo | Limiar |
| --- | --- | --- |
| Três tokenizers | `a1_1.tokenizers` | smollm2, qwen25, caracteres |
| Vocabulários | `a1_1.vocab_size` | smollm2=49152 nesta receita; qwen > 100k; caracteres=256 |
| Pares | `a1_1.pares` | ≥ 2 pares PT/EN com `n_tokens` e `razao_pt_en` |
| BPE | `a1_1.quebra_bpe` | `Segurado` em **mais de um** token nos HF |
| Testes | `pytest modulo-a1/testes -q -m "not modelo"` | passam |

O parágrafo cita **uma** razão PT/EN do JSON (não a da aula) e um split BPE concreto.

## CA1.2 — amostragem

| Critério | Campo | Limiar |
| --- | --- | --- |
| Greedy = `generate` | `a1_2.greedy_ids_iguais` | **true** |
| Warpers vs HF | `a1_2.warpers_hf` | os três Δ **< 1e-5** |
| T baixa = argmax | `a1_2.greedy_temperatura_baixa_igual_argmax` | **true** |
| Entropia | `a1_2.entropia` | H(T) **não decresce** com T |
| Config | `a1_2.config` | vocab, d, janela |
| Testes com modelo | `pytest modulo-a1/testes -q` | passam |

## Rubrica (0–10)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON próprio; razões PT/EN ancoradas; greedy igual; Δ warpers < 1e-5; parágrafo não recita o M01 no lugar da fórmula |
| 7–8 | Limiares ok; parágrafo vago (“PT gasta mais”) sem número do JSON |
| 5–6 | JSON de outro; copiou 1,40 da aula |
| 0–4 | Sem JSON; `generate` no lugar do laço; top-p “é o mesmo que top-k” |

A0/T4 `nao_calibrado` não derruba nota.
