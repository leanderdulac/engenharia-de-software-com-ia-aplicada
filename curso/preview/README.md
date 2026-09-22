# Preview local do curso

Servidor mínimo (Node.js + Express) para avaliar o pacote em `curso/` no navegador: navegação lateral, markdown renderizado, capas dos módulos, narrações TTS, intros Grok Imagine e índice de mídia.

Não altera labs nem exemplos. Só lê os arquivos Markdown e a pasta `curso/media/`.

## Requisitos

- Node.js 18 ou superior (22 recomendado, como no restante do repositório)

## Como rodar

### A partir da raiz do repositório

```bash
cd curso/preview
npm install
npm start
```

Equivalente sem mudar de diretório:

```bash
npm install --prefix curso/preview
npm start --prefix curso/preview
```

### A partir de `curso/preview`

```bash
npm install
npm start
```

Abra [http://localhost:3847](http://localhost:3847). A porta padrão é **3847**; para mudar:

```bash
PORT=8080 npm start
```

O script `npm run dev` é o mesmo que `npm start` (`node server.js`).

## O que o servidor faz

| Rota | Função |
| --- | --- |
| `/` | Interface (sidebar + painel de markdown) |
| `GET /api/page?path=README.md` | Lê um `.md` **somente** sob `curso/` (sem path traversal) |
| `GET /api/page?path=modulos/01.md` | Guia de um módulo |
| `GET /api/grok-videos` | Lista as intros Grok Imagine a partir de `media/videos/grok/manifest.json` |
| `GET /api/tts-audios` | Lista as narrações TTS a partir de `media/audios/tts/manifest.json` (`voice`, `rate`, `pitch`, `duration_seconds`, `src`, `vtt_src`) |
| `/media/…` | Arquivos estáticos de `curso/media/` (capas, intros Grok em `/media/videos/grok/modulo-0N-intro.mp4`, narrações em `/media/audios/tts/modulo-0N-narracao.mp3`, legendas em `/media/audios/tts/modulo-0N-narracao.vtt`) |

Caminhos relativos de imagem no markdown (`../media/...`, `./media/...`, `media/...` e `imagens/...` a partir de `media/README.md`) são reescritos para `/media/...`.

## Interface

A sidebar, em português, lista: Início, Syllabus, Trilha, Mapa, Avaliação, Guia do aluno, Guia do instrutor, Glossário, Lacunas, Mídia, **Intros Grok**, **Narrações TTS** e os Módulos 01–09. A capa hero aparece na home. A página de mídia, a rota `#/videos/grok` e a rota `#/audios` reproduzem os MP4 e MP3 versionados (além do índice de IDs HeyGen no markdown). Os players de áudio incluem `<track kind="captions" srclang="pt-BR">` e um link **Baixar legenda VTT**. Os guias `modulos/0N.md` e as páginas em `conteudo/modulo-0N/` ganham um player da narração daquele módulo.
