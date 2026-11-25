# Gabarito A13

2026-11-14T03:22:51Z (`epoch_unix` 1794626571), 4,817 s. sklearn 1.9.1. CPU.

Critério que zera: afirmar que VC é a teoria de generalização dos LLMs, ou igualar `n_params` LoRA à VC-dimensão.

| Item | Medido |
| --- | --- |
| 3 pontos | 8/8, estilhaça |
| 4 pontos | 14/16; falhas = XOR e o complemento |
| XOR | `linearmente_separavel=false` |
| C 0,01 → 100 | n_sv 68 → 58; margem 6,60 → 4,99; acc ~0,67 (overlap) |
| encoder | smollm2-135m-meanpool (576-d); TF-IDF 229-d declarado |
| TF-IDF SVM/RBF/logreg | 1,00 / 1,00 — léxico já é guardrail |
| embed SVM linear / RBF / logreg | 1,00 / 1,00 ; 0,938 / 1,00 ; 1,00 / 1,00 |
| Zhang SVM RBF | treino 1,00 / eval 0,50 (y embaralhado, 50% trocados) |
| Zhang MLP | treino 1,00 / eval 0,67 |
| Ponte A5 | 1,00 / 0,50; `termo_lora.vacuo=true` (inf); VC=3 com n=4: ε=1,55 vácuo |
| pytest A13 | 11 passed (`not modelo`) |

T4 / CIFAR Zhang / sentence-transformers: não. `h_proxy=460800` é plug-in, não VC do LoRA.

Parágrafo-modelo (não copiar no CA do aluno): o A5 interpolou n=4 com 460 800 params treináveis (R_emp=0, hold-out 0,50). A pergunta de 1971 é convergência uniforme na classe; com h_proxy ≥ n o termo é vácuo (inf); mesmo h=3 já dá ε=1,55. Zhang 2017: SVM/MLP decoram y aleatório (treino 1,00, eval 0,50–0,67). VC **não** é a teoria de generalização dos LLMs. SVM ainda serve como baseline/guardrail raso: neste domínio o linear em TF-IDF já faz 1,00 no hold-out.
