# Direitos: código da plataforma vs material do curso

O código em `curso/ead/` foi escrito para esta pós **como software de sala de aula local**. Não replica a interface de outro LMS e não transfere direitos sobre o material didáctico.

| Camada | Onde | Direitos |
| --- | --- | --- |
| Código da plataforma EaD (servidor, CSS, testes) | `curso/ead/` | Obra nova deste repositório. Não relinencia o tronco. |
| Markdown, capas, TTS, VTT, intros Grok, PDFs, labs | `curso/` (exceto `ead/`) e módulos na raiz | Continuam **CC BY-NC-ND 4.0** do tronco. A plataforma **lê** esses ficheiros; não os republica como obra própria. |
| Ilha Apache (`referencia/llm-course/`) | ramo Python opcional | Apache-2.0 do autor original; NOTICE intacto. A EaD só liga os README já vendored. |

GitHub Pages **não** hospeda esta plataforma (é estática, sem SQLite nem sessões). Preview em `curso/preview/` continua disponível e separado.

Não usar esta pasta como justificação para publicar o curso na internet.
