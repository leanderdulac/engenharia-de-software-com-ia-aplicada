# Módulo 09.2 — Preparação de datasets (Amplitude Seguros)

Labs **deste tronco** (JS/Python da pós): extração, limpeza, scoring e gate de PII. Não reescreva essas tools — rode as que já estão na pasta.

| Artefato local | Função |
| --- | --- |
| `extraction-to-jsonl-tool.js` / `extraction_to_jsonl_tool.py` | Documento → JSONL |
| `dataset-cleaning-balancing-tool.js` / `dataset_cleaning_balancing_tool.py` | Dedup / balanceamento Auto vs Saúde |
| `pii-scrubbing-gate-tool.js` / `pii_scrubbing_gate_tool.py` | Gate de PII da Amplitude |
| `data-relevance-scoring-tool.js` / `data_relevance_scoring_tool.py` | Score de relevância |
| `documentos-brutos/` | Imagens sintéticas do exercício |
| `dataset-amplitude-seguros.jsonl` | Demo curto |
| `privacy-preserving-finetuning-companion.md` | Companion de privacidade (Presidio, DP, etc.) |

Guia do módulo: [`curso/modulos/09.md`](../../curso/modulos/09.md). Missão: `Atividade 2 - Módulo 2.pdf` **ou** checkpoint C09.2.

## Checklist de governança (antes de treinar)

Complementa o gate da Amplitude; ideias alinhadas ao curso companheiro (Apache-2.0, isolado). Não substitui o `pii-scrubbing-gate-tool`.

- [ ] **PII:** o gate local desta pasta passou; revisão humana anotada (scanner automático é cobertura baixa).
- [ ] **Provenance:** origem, licença, finalidade e responsável escritos (mesmo para sintético).
- [ ] **Manifesto:** checksum dos JSONL + transformações (OCR, dedup, split).
- [ ] **Splits:** por entidade/tempo (apólice, segurado, documento) — não só shuffle de linhas.
- [ ] **Leakage:** a mesma pessoa/recibo não está em treino e teste; schema Auto vs Saúde discriminado.
- [ ] Brutos e pesos **fora** do Git; logs sem colar CPF/e-mail.

## Vendor Apache (`auditar_dataset`)

Scanner + manifesto do curso companheiro, **sem** misturar código Apache nesta pasta:

- Tool: [`referencia/llm-course/tools/auditar_dataset.py`](../../referencia/llm-course/tools/auditar_dataset.py)
- Como rodar: [`referencia/llm-course/README.md`](../../referencia/llm-course/README.md)
- Texto do gate: [`referencia/llm-course/docs/GOVERNANCA-DE-DADOS.md`](../../referencia/llm-course/docs/GOVERNANCA-DE-DADOS.md)
- Atribuição: [`curso/ATRIBUICOES-llm-course.md`](../../curso/ATRIBUICOES-llm-course.md)

Opcional depois do gate Amplitude: gerar o JSON de manifesto com a tool vendored e anexar ao C09.2. Exit code `2` = PII encontrado — isso é o exercício, não um “lab quebrado”.
