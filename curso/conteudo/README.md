# Conteúdo das aulas

Este diretório é o **texto didático** da pós-graduação: o que a pessoa lê (e o que a narração de áudio/vídeo comprime). Não substitui os labs. Complementa os guias de [`curso/modulos/`](../modulos/), que continuam sendo o mapa operacional (objetivos, checklist, pastas).

Os vídeos **não** estão neste Git. Os IDs HeyGen ficam em [`curso/media/videos/heygen-ids.json`](../media/videos/heygen-ids.json). As capas versionadas estão em [`curso/media/imagens/`](../media/imagens/).

## Como texto, áudio e vídeo se encaixam

Cada módulo tem três camadas. Elas contam a **mesma** história, em profundidades diferentes.

| Camada | Arquivo | Para quê | Duração típica |
| --- | --- | --- | --- |
| Texto da aula | `modulo-0N/aula.md` | Ler com calma, com caminhos reais, armadilhas e exercício | 1.500–3.000 palavras (~10–20 min de leitura) |
| Roteiro falado | `modulo-0N/roteiro-narracao.md` | Gravar áudio ou vídeo; português falado, frases curtas | ~450–700 palavras (3–5 min) |
| Metadados | `modulo-0N/meta.json` | Título, duração, caso âncora, capa | — |
| Guia operacional | [`modulos/0N.md`](../modulos/01.md) | Objetivos, mapa de labs, checklist, projeto | Não é aula: é o “o que fazer” |
| Vídeo HeyGen | IDs em [`media/videos/heygen-ids.json`](../media/videos/heygen-ids.json) | Abertura visual do módulo (fora do Git) | peça curta de abertura |

Fluxo sugerido para o aluno:

1. Abrir o [guia do módulo](../modulos/) e a capa.
2. Ler `aula.md` (ou ouvir o áudio gerado a partir do roteiro).
3. Ir para a pasta real do lab e **trabalhar no template** (M01–M03) ou no snapshot (M04) / ferramenta (M07–M09).
4. Só então abrir o gabarito `-z` ou o `output-exemplo-*`.
5. Fechar o checklist do guia.

O vídeo HeyGen, quando a plataforma da pós o exibir, é a porta de entrada emocional — não o substituto do texto nem do lab.

## Índice dos nove módulos

| # | Pasta | Texto | Caso âncora |
| --- | --- | --- | --- |
| 01 | [`modulo-01/`](./modulo-01/aula.md) | [aula](./modulo-01/aula.md) · [roteiro](./modulo-01/roteiro-narracao.md) | TF.js, Duck Hunt, RAG Neo4j |
| 02 | [`modulo-02/`](./modulo-02/aula.md) | [aula](./modulo-02/aula.md) · [roteiro](./modulo-02/roteiro-narracao.md) | Gateway, consultas médicas, Cypher |
| 03 | [`modulo-03/`](./modulo-03/aula.md) | [aula](./modulo-03/aula.md) · [roteiro](./modulo-03/roteiro-narracao.md) | CipherSuite MCP, customers MCP |
| 04 | [`modulo-04/`](./modulo-04/aula.md) | [aula](./modulo-04/aula.md) · [roteiro](./modulo-04/roteiro-narracao.md) | Notas API + **OpsPilot** |
| 05 | [`modulo-05/`](./modulo-05/aula.md) | [aula](./modulo-05/aula.md) · [roteiro](./modulo-05/roteiro-narracao.md) | Pix App, CFP Platform, BragBot |
| 06 | [`modulo-06/`](./modulo-06/aula.md) | [aula](./modulo-06/aula.md) · [roteiro](./modulo-06/roteiro-narracao.md) | **Nexus** (12 labs) |
| 07 | [`modulo-07/`](./modulo-07/aula.md) | [aula](./modulo-07/aula.md) · [roteiro](./modulo-07/roteiro-narracao.md) | **RouteWise** (10 ferramentas) |
| 08 | [`modulo-08/`](./modulo-08/aula.md) | [aula](./modulo-08/aula.md) · [roteiro](./modulo-08/roteiro-narracao.md) | **TrialForge** |
| 09 | [`modulo-09/`](./modulo-09/aula.md) | [aula](./modulo-09/aula.md) · [roteiro](./modulo-09/roteiro-narracao.md) | **Amplitude Seguros** |

Caminhos de lab neste índice e nas aulas são relativos à **raiz do repositório**.

## Convenções deste material

- **Português brasileiro.** Tom profissional e próximo, como aula de pós — não manual de API e não post de blog.
- **Pastas reais.** Só citamos o que existe neste clone. Se o README interno de um lab contradiz o disco (isso acontece nos Módulos 02, 03 e 05), o guia em `curso/modulos/` e esta aula prevalecem. Não inventamos `tests/`, PDFs ou subpastas ausentes.
- **Template vs gabarito (M01–M03).** Trabalhe em `*-template`. Abra `*-z` depois da tentativa. Nos Módulos 04–09 o padrão muda: snapshots cumulativos (OpsPilot), labs Python (Nexus), prompts/canvas (RouteWise, TrialForge, Amplitude).
- **Caso âncora.** OpsPilot, Nexus, RouteWise, TrialForge e Amplitude Seguros carregam o módulo inteiro. Não misture casos no mesmo entregável.
- **Links externos.** Só os que já estão no [README da raiz](../../README.md), no [syllabus](../syllabus.md) ou nos READMEs dos módulos. Se um paper ou ferramenta não estiver lá, trate como fora de escopo.
- **Código dos labs.** Estas aulas **não** modificam exemplos. Elas apontam. O exercício de fixação pede evidência sua (comando, trecho, print, Cypher), não um patch neste repositório.
- **Capa.** Cada `aula.md` abre com a imagem `../../media/imagens/modulo-0N-capa.png`.
- **Roteiro.** Começa com um comentário HTML `<!-- titulo: Módulo 0N — ... -->`. Sem tabelas Markdown. Frases curtas, para ser lido em voz alta.

## O que este diretório não é

- Não é ementa ([syllabus.md](../syllabus.md)).
- Não é rubrica ([avaliacao.md](../avaliacao.md)).
- Não é mapa pasta→lab ([mapa-do-repositorio.md](../mapa-do-repositorio.md)).
- Não é lista de lacunas ([lacunas-e-proximos-passos.md](../lacunas-e-proximos-passos.md)) — mas as aulas **avisam** as armadilhas documentadas lá (README “article generator”, pasta `modulo04-agentes-autonomos/` inexistente, pesos LoRA fora do Git, etc.).

Se um termo da aula parecer novo, consulte o [glossário](../glossario.md). Se o ambiente quebrar, [`troubleshooting/`](../../troubleshooting/) e o [guia do aluno](../guia-do-aluno.md).
