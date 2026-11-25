# Gabarito A14

2026-11-18T14:26:05Z (`epoch_unix` 1795011965), 0,124 s. sklearn 1.9.1. CPU. Torch ausente nesta bancada (A14 é numpy/sklearn).

Zera: n_eval A5 = 6; aula = adaptação do Lindholm; copiar PDF.

| Item | Medido |
| --- | --- |
| A5 1/2 Wilson | [0,095 ; 0,905], bootstrap [0 ; 1], `vacuo_pratico=true` |
| A5 se n=6 (não medido) | Wilson [0,188 ; 0,812] |
| A13 Zhang 3/6 | mesmo intervalo n=6 |
| A7 3/8 | Wilson [0,137 ; 0,694] |
| SelectKBest vazou | 0,778 vs 0,704 (Δ +0,074) |
| duplicata k-NN1 | 0,600 → 0,791 (treino 1,00) |
| 5-fold | 0,812 / 0,875 / 0,688 / 0,625 / 0,938 ; média 0,788 sd 0,130 |
| poly | treino cai 0,299 → 0,066; eval U com mínimo no grau 4 (0,187) e 1,247 no 16 |
| k-NN | treino 1,00 (k=1) → 0,79 (k=21) |
| ridge α=0,01 | eval 0,173 vs OLS 0,515 |
| features p=40=n | pico mse_eval 4,98; desceu depois |
| pytest A14 | ver corrida local |

PDF do smlbook não baixado. Figuras Belkin/Nakkiran não copiadas.
