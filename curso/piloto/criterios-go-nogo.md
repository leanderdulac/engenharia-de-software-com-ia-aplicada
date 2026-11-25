# Go / no-go para lançar o piloto acompanhado

Decisão do **coordenador**. Este ficheiro não lança nada.

## Go (todos)

1. `npm test --prefix curso/preview` passou nesta máquina/CI.
2. `node --test curso/avaliacao-colaboracao/verificar.test.mjs` passou; vazamento de PII **não** aprova.
3. `npm run check --prefix curso/preview` sem FAIL de link interno.
4. Preview local abre home, um módulo, uma aula, recarga hash, um PDF `/arquivos/`.
5. [Matriz](./matriz-prontidao.md) marca o recorte da turma (não precisa de M01–M09 verdes).
6. Consentimento e LMS prontos **na instituição** (não neste Git).
7. Coordenador leu [`../licencas/LEIA-ME.md`](../licencas/LEIA-ME.md) e **não** ligou Pages público sem autorização.

## No-go (qualquer um)

- Preview serve `.md` como HTML cru, CSS parte em rota profunda, ou PDF vira JSON.
- C-COLAB ainda dá “aprovado” com CPF no audit.
- Recorte da turma depende de GPU / Vertex / Groq **sem** caminho bloqueado documentado.
- Pedido para recrutar alunos ou pagar serviço a partir deste repo.
- Publicar adaptações (Pages, apostila pública) sem autorização dos titulares.

## Não é go

- URL histórica here.now.
- “O build passou” sem o e2e (quando há Chrome) **e** sem o instrutor abrir o preview uma vez.
- Nota de maturidade numérica inventada.
- Dry-run técnico tratado como evidência de aprendizagem.
