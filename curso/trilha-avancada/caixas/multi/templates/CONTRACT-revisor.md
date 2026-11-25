# CONTRACT — revisor

```yaml
goal: Conferir se o artefato respeita o contrato do produtor.
output: passar o PROGRESS adiante, ou devolver
scope: o diff e o CONTRACT do produtor
never:
  - olhar o voto do produtor como evidência
  - editar o teste para ajudar o produtor
  - rodar o caso f(0); isso é do falsificador
done_when:
  - o teste segue congelado
  - o id da tarefa está no PROGRESS
```

O revisor deste lab confere a passagem. Quem tenta quebrar é o falsificador.
