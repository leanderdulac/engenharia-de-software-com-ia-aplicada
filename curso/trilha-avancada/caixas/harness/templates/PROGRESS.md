# PROGRESS.md

Estado fora da janela de contexto. Um commit por etapa. A compactação do chat não apaga este arquivo.

## done

- ids que o sensor já marcou verde (não os que o agente «lembra»)

## current

- id em curso agora

## decisions

- campos v2 em snake_case; códigos de erro v1 ficam
- máscara de treino só nos tokens do assistente (A4); o prompt do usuário não entra na perda

## dead ends

- inventar streaming em `export_claims`
- regravar uma função já verde com outro esquema de nome

## blocked

- `export_claims`: a decisão de streaming não está no contrato; escalar, não inventar
- mesmo erro duas vezes (ver EXIT): parar e registrar o motivo
