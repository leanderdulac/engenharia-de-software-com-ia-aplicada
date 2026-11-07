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
| `HOST` | `0.0.0.0` |
| `PORT` | o da plataforma (`$PORT`) |
| `EAD_TRUST_PROXY` | `1` se houver proxy (Render, nginx) |

Auto-registo fica **fechado**. Abra só com `EAD_OPEN_SIGNUP=1` se a turma for mesmo pública na rede privada.

## Operação

```bash
cd curso/ead
npm ci
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
