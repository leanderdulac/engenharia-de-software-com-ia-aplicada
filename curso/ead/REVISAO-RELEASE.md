# Revisão técnica de release (piloto privado)

Registo para o coordenador. Não é aprovação de pull request, não é merge e não é certificação de produção.

Data da revisão local: 2026-11-07.

## Destino das bases

| PR | Branch | Base | Integração |
| --- | --- | --- | --- |
| #13 | `cursor/estabilizacao-piloto-2f8f` | `main` | Primeiro, se o coordenador aceitar publicar o diff no repositório público |
| #14 | `cursor/ead-plataforma-2f8f` | `cursor/estabilizacao-piloto-2f8f` | Depois do #13. A base move com o tip do #13. Não foi feito rebase |

SHAs anteriores a esta rodada: #13 `89d850ae0ff42a490889fa214e3033291f5db3b9`, #14 `7db1e5524ecc240e24b069c5b40069cd2e53e169`, `main` `2471a076216bad94277a60160865879015bdd7db`.

## Portão de conteúdo (reversível, mesma stack)

Fechar o auto-registo não protegia mídia nem o preview.

- Sala: `GET /media/*` e `GET /arquivos/*` respondem 401 sem sessão. Aula, catálogo e glossário já exigiam sessão.
- Preview: omissão continua aberto (testes e leitura local). `PREVIEW_REQUIRE_AUTH=1` exige o cookie `ead_sid` da mesma SQLite (`EAD_DATA_DIR` ou `PREVIEW_AUTH_DB`) em `/`, API, markdown, `/media` e `/arquivos`. `NODE_ENV=production` recusa escutar sem o flag e sem o caminho da base.
- CSS e JS do casco do preview não carregam o texto do curso. Desligar o flag volta ao comportamento anterior.
- Não houve mudança de Express/SQLite nem serviço cloud.

Rotas que continuam sem sessão, de propósito: `/`, `/entrar`, `/registar` (fechado em produção), `/redefinir`, `/ajuda`, `/privacidade`, `/healthz`, `/readyz`, `/verificar/:code` (nome e código, sem markdown nem ficheiro).

## CI que estava vermelho

- Job `ead`: `Cannot find package 'marked'` porque `curso/preview/lib/markdown.mjs` resolve o pacote em `curso/preview/node_modules`. O workflow passa a correr `npm --prefix curso/preview ci` antes dos testes da sala.
- Job `curso`: `npm ci` no submódulo `routewise-danger-demo` falha porque o `package-lock.json` existe só na cópia local (`??`, não está no commit do submódulo). O passo usa `npm install --ignore-scripts` quando o lock não vem no checkout. Não foi feito commit dentro do submódulo nem force-push.

## O que não foi feito

- Merge, review de aprovação no GitHub, alteração de branch protection, rebase, amend, force-push.
- Deploy, Pages, URL pública, recurso cloud, e-mail, recrutamento.
- Mudança de licença. O tronco continua CC BY-NC-ND 4.0.

## Risco de integrar em `main`

O repositório é público. O workflow `pages-preview.yml` só corre por `workflow_dispatch` e o input `deploy` vem `false`. Merge **não** publica Pages sozinho. Dispatch com `deploy=true` publicaria o preview estático (markdown e mídia) e deve permanecer desligado.

Integrar na branch default ainda coloca o diff (incluindo código que lê o material e ficheiros de adaptação) no GitHub público. Isso é decisão do coordenador, não deste registo. Recomendação desta rodada: **NO-GO para merge em `main`**. O pacote localhost abaixo não substitui essa decisão e não foi anexado ao pull request, porque o repositório é público e o arquivo contém o material.

## Pacote localhost (sem hospedagem)

Arquivos para copiar ao computador do operador, não para abrir a partir desta VM:

- `/opt/cursor/artifacts/lms-localhost.tar.gz`
- `/opt/cursor/artifacts/lms-localhost.zip`

SHA-256 (gerados depois do portão de restore):

- `2af438de8543df66dffb5c6bab5ae336393bb8ae8f3822b2980e66f9914e0976` tar.gz
- `5c2cd55999960f6a7d03a8cc090dbc87c8832138baed50ee5bddec740e928d33` zip

O smoke funcional correu no mesmo software. Estes hashes são o arquivo final, que só acrescenta uma frase no guia sobre `EAD_DATA_DIR` já definido na sessão.

O processo por omissão escuta `127.0.0.1`. O guia no pacote é `README-LOCAL.md`. Não há senha de administrador dentro do arquivo. `npm ci` do preview, neste ambiente, reportou 2 avisos de `npm audit` (1 moderate, 1 high); não foi aplicado `npm audit fix`.

Smoke do arquivo extraído em `/tmp/lms-smoke3` (Node 22.23.4): `npm ci` nos dois prefixos, migração schema 2, admin criado por variável de ambiente, escuta confirmada em `127.0.0.1:3858` (porta de teste, não a 3850 do guia). Anónimo em `/media/.../curso-capa-hero.png` → 401. Depois do login: `/aula/m01-aula` 200 com o título do módulo 01 (21 057 bytes de HTML), capa PNG 244 684 bytes, áudio MP3 2 067 840 bytes. Backup gravado, processo parado, restore de caminho inexistente recusado, restore do backup com 1 utilizador. Esse endereço só existiu nesta máquina de verificação.
