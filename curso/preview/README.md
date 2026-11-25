# Preview do curso

Servidor mínimo (Node.js + Express) e **build estático** para avaliar o pacote em `curso/` no navegador: navegação lateral, markdown renderizado, capas, narrações TTS, intros Grok Imagine, PDFs das missões M07–M09 e índice de mídia.

Não altera labs nem exemplos. Não regenera TTS/vídeo/capas. Só lê Markdown, `curso/media/` e PDFs **já versionados** no repositório.

O preview **não** é publicação jurídica autorizada. CC BY-NC-ND 4.0 pode impedir distribuir adaptações (incluindo HTML gerado) ao público. Ver [`../licencas/LEIA-ME.md`](../licencas/LEIA-ME.md). GitHub Pages **não** é ligado por este repositório — o workflow só constrói o artefato.

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

O script `npm run dev` é o mesmo que `npm start` (`node server.js`). O servidor escuta em `0.0.0.0:$PORT` (padrão 3847).

### Build estático (GitHub Pages — verificável, sem publicar)

```bash
npm run build --prefix curso/preview
```

Gera `curso/preview/dist/` (não versionado): HTML/JS/CSS relativos, JSON das páginas, mídia copiada, PDFs das missões em `dist/arquivos/`. Abra `dist/index.html` ou sirva a pasta. Hash routing (`#/modulos/01.md`) sobrevive a recarga.

Para um site de projeto no GitHub Pages (`https://<user>.github.io/<repo>/`):

```bash
GITHUB_PAGES=1 GITHUB_REPOSITORY=leanderdulac/engenharia-de-software-com-ia-aplicada npm run build --prefix curso/preview
```

Isso **não** habilita Pages na conta. O workflow `.github/workflows/ci-curso-piloto.yml` constrói e testa. Um workflow separado (`pages-preview.yml`) só faz deploy se alguém com permissão disparar `workflow_dispatch` **e** Pages (source = GitHub Actions) já estiver habilitado — e só depois de revisão jurídica. URL persistente **não** é afirmada aqui.

URL histórica `brave-jubilee-jhza.here.now` (here.now, ~24 h) **não** é o preview atual.

### Testes de regressão

```bash
npm test --prefix curso/preview
npm run check --prefix curso/preview
npm run e2e --prefix curso/preview   # Chrome headless via DevTools; SKIP se não houver Chrome
```

`check` falha em link interno quebrado. `check:external` classifica HTTP **403** como bloqueado (≠ 404) e **não** falha o job por 403.

## O que o servidor faz

| Rota | Função |
| --- | --- |
| `/` | Interface (sidebar + painel de markdown) |
| `GET /api/page?path=README.md` | Lê um `.md` **somente** sob `curso/` (sem path traversal) |
| `GET /api/page?path=modulos/01.md` | Guia de um módulo |
| `GET /api/grok-videos` | Lista as intros Grok Imagine a partir de `media/videos/grok/manifest.json` |
| `GET /api/tts-audios` | Lista as narrações TTS a partir de `media/audios/tts/manifest.json` (`voice`, `rate`, `pitch`, `duration_seconds`, `src`, `vtt_src`) |
| `/media/…` | Arquivos estáticos de `curso/media/` (capas, intros Grok, narrações MP3, legendas VTT) |
| `/arquivos/…` | PDFs **do repositório** citados no pacote (missões M07–M09). `Content-Type: application/pdf`. Não serve `.md` nem arquivos fora do Git. |
| `GET /modulos/01.md` | **Não** renderiza markdown como HTML. Com `Accept: text/html` redireciona para `/#/modulos/01.md`. Com `?raw=1` devolve `text/markdown`. |

Caminhos relativos de imagem no markdown (`../media/...`, `./media/...`, `media/...` e `imagens/...` a partir de `media/README.md`) são reescritos para `/media/...`.

## Interface

A sidebar, em português, lista o pacote (incluindo C-COLAB, licenças e protocolo de piloto), mídia e os Módulos 01–09. JS/CSS são caminhos **relativos** (`./app.js`, `./styles.css`) para não quebrar em GitHub Pages nem em recarga de rota profunda. A capa hero aparece na home. Players de áudio incluem `<track kind="captions" srclang="pt-BR">`. Escape fecha o menu. PDFs abrem em nova aba via `/arquivos/`.

Não ouvimos os MP3/MP4 nesta estabilização: a evidência de acessibilidade é o arquivo VTT no disco + o `<track>` no HTML. HeyGen fora do Git não tem transcrição aqui.
