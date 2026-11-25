# Instalação privada (uma instância)

Esta sala pode correr como LMS da turma **neste** servidor. Não é cluster, não é GitHub Pages e **não** deve ser publicada na internet: o material do curso é CC BY-NC-ND 4.0.

Topologia suportada: **um processo Node + um ficheiro SQLite num disco que sobrevive a restart**. Sem réplicas. Sem SMTP.

## O que o arranque exige em produção

`NODE_ENV=production` recusa subir se faltar algum destes:

| Variável | Valor |
| --- | --- |
| `EAD_SECURE_COOKIES` | `1` (TLS na borda; o processo escuta HTTP) |
| `EAD_DATA_DIR` | directório persistente, fora do disco efémero do contentor |
| `EAD_SEED_DEMO` | ausente. Seed de demonstração não corre em produção |
| `HOST` | omissão `127.0.0.1` (só esta máquina). `0.0.0.0` só se um proxy privado na mesma rede for mesmo o destino |
| `PORT` | o da plataforma (`$PORT`) |
| `EAD_TRUST_PROXY` | `1` se houver proxy (Render, nginx) |
| `EAD_ALLOWED_HOSTS` | omissão `127.0.0.1,localhost,[::1]`. Um nome atrás do proxy tem de entrar aqui; Host ou Origin fora da lista é recusado |

Auto-registo HTTP fica **fechado** salvo o valor exacto `EAD_OPEN_SIGNUP=1`. Isso vale para GET e POST `/registar`, com `NODE_ENV` de produção, de desenvolvimento ou ausente. `0`, vazio ou qualquer outro texto mantém fechado. O opt-in `1` é deliberado (turma pública na rede privada). `create-admin`, `create-user` e o seed de laboratório não passam pelo formulário. Fechar o registo **não** protege ficheiros: `/media` e `/arquivos` da sala exigem sessão. O preview, noutro processo, só fica fechado com `PREVIEW_REQUIRE_AUTH=1` e a **mesma** base (`EAD_DATA_DIR` ou `PREVIEW_AUTH_DB`). Em `NODE_ENV=production` o preview recusa arrancar sem isso. CSS e JS do casco do preview não contêm o material; páginas, API, markdown, mídia e PDF sim.

## Dependências exactas para subir os dois processos

Node **≥ 22.23.4** (o workflow usa 22.23.4; o Inspector do módulo 3 usa 24.22.1 à parte). Sem SMTP, sem serviço cloud criado por este repositório.

```bash
npm --prefix curso/preview ci
npm --prefix curso/ead ci
```

O render de aulas importa `marked` a partir de `curso/preview/lib`. Sem `npm ci` no preview, a sala responde 500 nas aulas mesmo com as dependências do EaD instaladas.

Preview no mesmo host (cookie `ead_sid` não é por porta):

```bash
NODE_ENV=production PREVIEW_REQUIRE_AUTH=1 EAD_DATA_DIR=/var/ead \
  HOST=0.0.0.0 PORT=3847 npm --prefix curso/preview start
```

HTTPS fica na borda (nginx/Caddy). O processo escuta HTTP. Não use a VM do agente como disco durável: `EAD_DATA_DIR` tem de ser um volume que o operador controla.

## Operação

```bash
npm --prefix curso/preview ci
npm --prefix curso/ead ci
cd curso/ead
NODE_ENV=production EAD_SECURE_COOKIES=1 EAD_DATA_DIR=/var/ead \
  EAD_ADMIN_EMAIL=admin@local.test EAD_ADMIN_PASSWORD='…' npm run create-admin
NODE_ENV=production EAD_SECURE_COOKIES=1 EAD_DATA_DIR=/var/ead \
  EAD_TRUST_PROXY=1 HOST=0.0.0.0 npm start
```

Saúde: `GET /healthz` (processo) e `GET /readyz` (SQLite + versão de schema). O processo trata `SIGTERM` e fecha o ficheiro.

```bash
npm run check
npm run backup -- /var/ead/ead-$(date +%F).sqlite
# pare o processo antes de restaurar
node src/cli.mjs restore /var/ead/ead-2026-11-07.sqlite
```

Contas de aluno/instrutor sem formulário público:

```bash
EAD_USER_EMAIL=… EAD_USER_NAME=… EAD_USER_PASSWORD=… EAD_USER_ROLE=aluno node src/cli.mjs create-user
EAD_RESET_EMAIL=… node src/cli.mjs reset-token
```

O token imprime-se **uma vez** no terminal. Não vai para e-mail (SMTP desligado). Vale 30 minutos.

## O que isto não faz

- Não escala na horizontal (SQLite + disco local).
- Não envia e-mail, não faz SSO, não cobra.
- Não publica o curso. Um blueprint Render na raiz do repositório **não** foi adicionado de propósito: sincronizá-lo criaria um serviço acessível com material ND.
