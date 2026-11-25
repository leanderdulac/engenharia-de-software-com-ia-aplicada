# Execução da simulação tática

Simulação didática. Não é LLM. Sem API. `llm_real` = `nao_calibrado`.

- Quando: 2026-11-25T02:57:47Z (mesma leva da caixa multi-harness; o script é determinístico)
- Comando, a partir de `curso/trilha-avancada`:

```bash
python caixas/tatica/lab/simular.py
```

Saída:

```
A  entregues 8.0  violacoes 5.4 ± 1.2312  dup 1.2 ± 0.6959  seguinte 9.4 ± 1.2312  passos 43.4 ± 5.7436  tentados 6.35  aceitos 5.4  teste 0.95  regra 0.0  revisor 0.0  escalados 0.0
B  entregues 8.0  violacoes 5.4 ± 1.2312  dup 3.15 ± 1.1367  seguinte 9.4 ± 1.2312  passos 46.65 ± 7.5969  tentados 6.35  aceitos 5.4  teste 0.95  regra 1.95  revisor 0.0  escalados 0.0
C  entregues 8.0  violacoes 0.0 ± 0.0  dup 0.0 ± 0.0  seguinte 4.0 ± 0.0  passos 35.85 ± 1.7554  tentados 6.35  aceitos 0.0  teste 0.95  regra 1.95  revisor 5.4  escalados 0.65
```

O JSON ao lado é a fonte. Vinte seeds `0..19`. Desvio amostral (n−1).
