# Execução da simulação

Simulação didática. Não é LLM. Sem API.

- Quando: 2026-11-23T02:14:56Z
- Onde: VM desta trilha, Python 3 da imagem
- Comando, a partir de `curso/trilha-avancada`:

```bash
python caixas/harness/lab/simular.py
```

Saída dessa rodada:

```
A relatado 12.0  concluidas 3.2 ± 0.7678  escopo 3.3  desperdicio 9.2
B relatado 10.1  concluidas 10.1 ± 0.8522  escopo_aplicado 0.0  escopo_tentado 2.6  desperdicio 4.8  escalados 1.9
```

O JSON ao lado (`medicao.json`) é a fonte. Desvio = amostral (n−1), 20 seeds `0..19`. `llm_real` = `nao_calibrado`. Os 40/11/39 do artigo não estão neste arquivo.
