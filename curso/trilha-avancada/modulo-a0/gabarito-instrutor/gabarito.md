# Gabarito A0 (instrutor)

[`../execucao/run-vm.md`](../execucao/run-vm.md). 2026-11-12T14:42:41Z (`epoch_unix=1794494561`), `segundos_total=9.864`.

| Item | Medido |
| --- | --- |
| modelo | SmolLM2-135M, 134 515 008 params |
| p50 c1 / c2 | 0,172 / 0,163 s (±20% true) |
| p95 c1 | 0,186 s |
| tok/s c1 | 46,0 |
| pegada | 538 MB |
| RSS pico | 993 MB |
| envelope treino | 2152 MB |
| bitsandbytes | null |
| pytest | 3 sem modelo + 1 com modelo |

Aluno que copia 0,172 sem JSON próprio está errado. Aluno que marca T4 calibrado nesta CPU está errado.
