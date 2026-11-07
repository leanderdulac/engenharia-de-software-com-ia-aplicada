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

Rotas que continuam sem sessão, de propósito: `/`, `/entrar`, `/registar` (fechado salvo `EAD_OPEN_SIGNUP=1` exacto; `0`, ausente ou outro valor recusam GET e POST), `/redefinir`, `/ajuda`, `/privacidade`, `/healthz`, `/readyz`, `/verificar/:code` (código, sem nome, e-mail, markdown nem ficheiro).

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

## Segurança desta rodada (não é pentest)

Audit npm em 2026-11-07T16:23:12Z, `npm ci` limpo só com `package.json` + lock:

| Escopo | Antes | Depois | Notas |
| --- | --- | --- | --- |
| `curso/preview` runtime (70 prod) | high `body-parser` &lt;1.20.9 ([GHSA-27r3-jxmh-p828](https://github.com/advisories/GHSA-27r3-jxmh-p828), DoS de corpo comprimido); moderate `qs` 6.16.0 ([GHSA-6pq8-jhm2-2vcw](https://github.com/advisories/GHSA-6pq8-jhm2-2vcw), `stringify` com `arrayFormat: comma`) | 0 conhecidas | `body-parser@1.20.9`, `qs@6.16.2`, ambos transitivos de `express@4.22.3`. Sem `--force` e sem override. O `qs` vulnerável não era chamado pelo formulário (`extended: false`); o `body-parser` sim, no POST. |
| `curso/ead` runtime (70 prod) | 0 conhecidas no mesmo instante | 0 conhecidas | Já estava em 1.20.9 / 6.16.2 |

SBOM CycloneDX: `curso/preview/sbom.cdx.json` e `curso/ead/sbom.cdx.json` (npm 10.9.9). Zero avisos conhecidos nesse instante não significa ausência de falhas.

Controles novos no processo: `Host` limitado a loopback (ou `EAD_ALLOWED_HOSTS`), `Origin` cruzada recusada em POST, sem CORS aberto, `next` só caminho local, HTML de markdown sem `javascript:`/`data:`/URL `//`, CSV com prefixo de fórmula, realpath contra symlink, `.env`/sqlite/log não servidos, `/readyz` só `ok`+`service`, comprovante público sem nome/e-mail, instrutor não emite token de outro staff, scrypt N=32768 com teto de parâmetros, base e backup `0600`/`0700`, rate limit de login/reset/registo/submissão/verificação. Suítes: preview 24/24 e sala 21/21 em Node 22.23.4 e 24.22.1.

## Auto-registo (correcção depois do pacote a5a6b217)

No pacote `a5a6b217`, com `EAD_OPEN_SIGNUP=0` e `NODE_ENV` ausente, GET `/registar` respondia 200 e mostrava nome, e-mail e senha, com texto a dizer que o fecho era só em produção. POST com CSRF válido respondia 403 e não criava conta, mas gravava uma linha em `login_attempts`. Sem a variável, em development, o POST criava o aluno (303).

Agora só `EAD_OPEN_SIGNUP=1` abre GET e POST. `0`, ausente ou qualquer outro valor fecha os dois, antes de escrever na base, em development, sem `NODE_ENV` e em production. Não há rota `/api/registar`. `create-admin`, `create-user` e o seed continuam na CLI. A base instalada continua em `curso/ead/data/ead.sqlite`.

Pacote seguinte, sem a base: tar `d89b7f04bcd68b7e7186a6f8e1d06edc502d0e3f07798a6b4c370b2e884b200d`, zip `6de9b7fede356809377a9f74a4100d650db9364c25777a4c0ea673af07c3154d`. Overlay para quem já instalou o `a5a6b217`: `lms-signup-patch-a5a6b217.tar.gz` com SHA-256 `62a36d5f204f507df91fddd45a2696c1f3d11e5854a5c6c092c01af339105919`. Smoke deste arquivo em `127.0.0.1:3863`, `NODE_ENV` ausente: GET e POST `/registar` 403, sem formulário, 1 admin, 0 tentativas, login do admin a abrir o painel. A senha desse smoke não foi impressa.

## Pacote localhost (sem hospedagem)

O arquivo localhost não entra no GitHub. A cópia privada vai no store do agente; as partes de no máximo 20 MB são só o plano B de transferência. Checksums desta montagem, calculados depois do smoke:

- tar.gz `a5a6b217da597b91e65742c26f115cc78da61fc532f94e1d114333d47d6df7a8`
- zip `4da78d7e835681daeb598679468196e3f1ac7ee3ca0f6e2d0712a254414db2fe`

O processo por omissão escuta `127.0.0.1`. O guia no pacote é `README-LOCAL.md`. Não há senha de administrador dentro do arquivo. Depois da actualização de `body-parser` e `qs`, o `npm ci` limpo dos dois prefixos reportou 0 vulnerabilidades conhecidas em 2026-11-07T16:23:12Z.

Smoke anterior, do arquivo já substituído, em `/tmp/lms-smoke3` (Node 22.23.4, porta de teste 3858): também leu o MP3 de 2 067 840 bytes e recusou restore de caminho inexistente.

Smoke deste arquivo em `/tmp/lms-sec` (Node 22.23.4, porta de teste 3861, só nesta VM): o tar não trazia `node_modules`, `.git`, `.env` nem sqlite. `subir.sh` fez `npm ci` nos dois prefixos, migrou o schema 2 e escutou `127.0.0.1`. Anónimo na capa → 401. Depois do login: `/aula/m01-aula` 200 com o título do módulo 01 (21 057 bytes), PNG 244 684 bytes, backup gravado, processo parado. A senha desse admin ficou só na variável da sessão e não foi impressa. Esse endereço não é o computador do operador.
