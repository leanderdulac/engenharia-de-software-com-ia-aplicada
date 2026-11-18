# Plano de conteúdos originais substituíveis

Uso interno do coordenador. Não é autorização. Não envia nada a titulares.

Se a Unipds **não** obtiver permissão para redistribuir adaptações do material informado como CC BY-NC-ND 4.0, o piloto acompanhado ainda pode correr **no clone privado da turma** com o original. Para um **artefato público** (Pages, espelho, apostila), só publique o que for:

1. texto **original** desta pós (redação própria, casos âncora próprios), **ou**
2. material com licença que permita essa publicação (ex. ilha Apache, com NOTICE), **ou**
3. original CC BY-NC-ND **sem adaptar**, com atribuição.

## O que já é redação própria do pacote `curso/` (ainda sobre o tronco)

Guias, trilha, rubricas, C-COLAB, protocolo de piloto, este plano. Continua no tronco CC BY-NC-ND: **não** vira Apache por estar “novo”. Se o coordenador quiser um pacote público só-original, copie estes ficheiros para um repo **separado** com licença escolhida pelos titulares — isso é decisão humana, não deste PR.

## Substituições possíveis (se faltar autorização de adaptação)

| Peça atual | Substituição original (trabalho futuro, não feito aqui) | Quem autoriza |
| --- | --- | --- |
| `aula.md` / `roteiro-narracao.md` M01–M09 | Reescrever a aula em cima só dos labs (sem parafrasear slides de terceiros) | Unipds / docente |
| Capas, Grok, TTS, HeyGen | Gerar mídia nova com contrato que permita o uso pretendido, **ou** omitir mídia no pacote público | Unipds + termos do gerador |
| PDFs `Atividade` / `Exemplo` M07–M09 | Enunciados Markdown originais no pacote `curso/` | Docente da unidade |
| Labs `modulo01`–`09` com código de terceiros | Trocar por labs mínimos originais **ou** manter só o que tiver LICENSE permissiva ao lado | Titulares de cada lab |
| Duck Hunt / templates Fastify / CFP | Manter LICENSE local; não republicar como UniPDS | Autores originais |
| `referencia/llm-course/` | Já é Apache isolado; pode continuar público **nessa pasta** com LICENSE+NOTICE | Luciano de Oliveira Nunes (já via Apache) |

## O que **não** substituímos neste PR

- Não apagámos aulas originais.
- Não relicenciámos labs.
- Não gerámos mídia nova.
- Não afirmámos que “já pode vender o curso”.

## Ordem sugerida ao coordenador

1. Pedir por escrito (canal oficial, não este agente) autorização de **adaptação e redistribuição não comercial** do tronco, se o objetivo for Pages/apostila.
2. Enquanto não houver resposta: piloto **acompanhado**, clone privado, sem Pages público.
3. Se a resposta for não: publicar só a ilha Apache + um guia original curto que *aponta* para o repo privado, sem copiar as aulas.
