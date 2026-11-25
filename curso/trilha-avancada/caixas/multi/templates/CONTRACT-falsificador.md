# CONTRACT — falsificador

```yaml
goal: Quebrar a mudança com um caso que o teste congelado não roda.
output: verde, ou devolução ao produtor
scope: o caso f(0) == 0
never:
  - editar o teste congelado
  - declarar corrida; o contrato não tem sensor para ela
done_when:
  - f(0) == 0, e o teste congelado continua f(1) == 2
```

Corrida plantada que passa em `f(1)` e em `f(0)` escapa nos dois arranjos. O lab conta essa fuga. Não finge que o trio vê tudo.
