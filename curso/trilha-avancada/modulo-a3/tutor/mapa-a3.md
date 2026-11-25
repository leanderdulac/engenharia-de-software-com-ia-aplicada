# Mapa — A3

```
Use o tutor socrático com este mapa do A3. Não invente loss; peça ca3.json.
```

- **A. Shift:** o que `logits[:, :-1]` prediz? Por que treinar sem shift vaza o token atual?
- **B. Accumulation:** por que Δ < 1e-5 exige dropout off e o mesmo lote?
- **C. Envelope:** por que RSS 320 MB não contradiz envelope 0,4 MB do mini-modelo?
