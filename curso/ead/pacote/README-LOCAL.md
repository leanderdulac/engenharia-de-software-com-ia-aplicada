# Sala no seu computador (localhost)

Este pacote sobe a sala **só nesta máquina**. Não clona o repositório, não publica na internet e não cria serviço em nuvem. O endereço `http://127.0.0.1:3850/` existe apenas no computador onde o processo está a correr. Não é um site que outro computador abre.

O material do curso continua CC BY-NC-ND 4.0. Não redistribua este arquivo.

## Node.js

A sala usa `node:sqlite` (`DatabaseSync` e `backup()`, incluindo a opção `rate`). No changelog do Node 22.23.4, `backup()` entrou na linha 22 em **22.16.0**. Abaixo disso o comando de backup não existe.

| | Versão |
| --- | --- |
| Mínimo da API que este código importa | **22.16.0** |
| Versão em que o pacote foi extraído, instalado e fumado | **22.23.4** |

Confirme com `node -v`. O script recusa arrancar abaixo de 22.16.0.

## O que vem no arquivo

- `curso/ead` — sala, `package-lock.json`, migração (`src/cli.mjs`)
- `curso/preview` — só o que a sala importa para renderizar markdown (`lib/`) mais o leitor opcional; sem `node_modules`
- Aulas, guias, glossário, diagnóstico, mídia (capas, áudio, VTT, intros) e PDFs cujo nome começa por `Atividade`
- Trilha Python opcional em `referencia/llm-course` (texto Apache-2.0, não substitui os módulos)
- Verificador C-COLAB local, sem API paga

Não vem: `.git`, `node_modules`, base SQLite, `.env`, senhas, pastas de lab (`modulo01-…` e afins). A aula cita essas pastas; o texto e a mídia abrem sem elas. Os labs continuam no repositório completo, fora deste pacote.

## Subir

Na pasta deste pacote (a que contém `curso/` e `scripts/`):

```bash
chmod +x scripts/*.sh
./scripts/subir.sh
```

Na primeira vez o script corre `npm ci` em `curso/preview` e em `curso/ead`, migra a base para `curso/ead/data/ead.sqlite` e pede e-mail e senha de administração. A senha não é gravada no pacote. Mínimo 10 caracteres.

Sem perguntas, na mesma sessão de terminal (também não grave isto num ficheiro do pacote):

```bash
export EAD_ADMIN_EMAIL='voce@exemplo.local'
export EAD_ADMIN_PASSWORD='escolha-uma-senha-longa'
./scripts/subir.sh
unset EAD_ADMIN_PASSWORD
```

O script força `HOST=127.0.0.1` e a porta `3850` (mude com `PORT=3851` se a 3850 estiver ocupada). Se `EAD_DATA_DIR` já estiver definido na sessão, a base vai para essa pasta em vez de `curso/ead/data`. Abra no navegador **deste** computador: `http://127.0.0.1:3850/`.

Entre com o e-mail e a senha que acabou de definir. Auto-registo fica fechado quando `NODE_ENV=production`. Para esta máquina, o script **não** define produção: o registo público da página inicial continua desligado se exportar `EAD_OPEN_SIGNUP=0`. O script exporta `EAD_OPEN_SIGNUP=0`.

## Parar

Noutro terminal, na mesma pasta:

```bash
./scripts/parar.sh
```

Ou Ctrl+C no terminal que corre `subir.sh`.

## Backup e restore

Com a sala parada ou a correr (o backup abre outra ligação ao SQLite):

```bash
./scripts/backup.sh
```

O ficheiro fica em `curso/ead/data/backup-AAAA-MM-DD.sqlite`. Para repor, pare a sala e, a partir de `curso/ead` (um caminho em falta é recusado e a base actual fica como está):

```bash
EAD_DATA_DIR="$PWD/data" node src/cli.mjs restore data/backup-AAAA-MM-DD.sqlite
```

## Conta de aluno

Não há aluno embutido. Na pasta `curso/ead`, com a mesma `EAD_DATA_DIR`:

```bash
export EAD_DATA_DIR="$PWD/data"
export EAD_USER_EMAIL='aluno@exemplo.local'
export EAD_USER_NAME='Nome'
export EAD_USER_PASSWORD='outra-senha-longa'
export EAD_USER_ROLE=aluno
node src/cli.mjs create-user
unset EAD_USER_PASSWORD
```

`EAD_USER_ROLE=instrutor` cria instrutor. Administrador continua só em `create-admin`.

## Preview (opcional)

A aula já é renderizada pela sala. O leitor em `curso/preview` só deve subir com o mesmo cookie e a mesma base, e só em loopback:

```bash
HOST=127.0.0.1 PORT=3847 PREVIEW_REQUIRE_AUTH=1 \
  EAD_DATA_DIR="$PWD/curso/ead/data" \
  npm --prefix curso/preview start
```

Sem `PREVIEW_REQUIRE_AUTH=1` esse leitor entrega markdown e mídia sem sessão. Não o use assim fora de uma experiência que você controle.
