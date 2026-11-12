# A4 — Dados para SFT no nível do token

**Status:** esqueleto (não publicado). **Carga prevista:** 4 h. **Pré-requisito previsto:** A1 + M09 pasta 02.

O M09 já limpa JSONL, faz split por entidade e manifesto. Este módulo desce ao tensor: chat template, system prompt *como dado*, multi-turn, padding/truncamento, attention mask, EOS.

**Labs previstos:** JSONL Amplitude (uso privado da turma, sem republicar) + oasst1 → `input_ids`/`labels` com prompt em −100 (CA4.1); o mesmo conjunto com e sem system prompt, efeito medido depois do A5 (CA4.2).
