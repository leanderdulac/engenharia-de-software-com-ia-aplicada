# Execução da simulação multi-harness

Simulação didática. Não é LLM. Sem API. `llm_real` = `nao_calibrado`.

- Quando: 2026-11-25T02:57:47Z
- Comando, a partir de `curso/trilha-avancada`:

```bash
python caixas/multi/lab/simular.py
```

Saída:

```
U  escapam 4.75 ± 0.9665  plantados 5.25  barradas 0.0 ± 0.0  aplicadas 2.3  tentativas 2.3  passagens 0.0 ± 0.0  passos 22.55 ± 2.6253  escalados 0.0 ± 0.0
T  escapam 0.8 ± 0.4104  plantados 5.25  barradas 2.05 ± 0.9987  aplicadas 0.0  tentativas 2.05  passagens 15.9 ± 1.9167  passos 59.8 ± 5.2676  escalados 1.05 ± 0.8256
```

O JSON ao lado é a fonte. Vinte seeds `0..19`. Desvio amostral (n−1). A corrida plantada não entra nos sensores; o escape que resta no arranjo T é essa classe.
