# Sala de aula (LMS de uma instalação)

Plataforma desta pós, no mesmo repositório. Lê o pacote em `curso/` (módulos, capas, TTS, VTT, intros Grok, checkpoints de `avaliacao.md`). Não é o preview estático; não é GitHub Pages; não cobra matrícula.

Em `NODE_ENV=production` é um LMS de **uma instância privada**: migrações versionadas, backup, janela de turma, contas desactiváveis, token de senha sem e-mail, auditoria e healthcheck. Não é cluster nem SaaS. Deploy: [DEPLOY-PRIVADO.md](./DEPLOY-PRIVADO.md).

Código desta pasta ≠ direitos sobre o material didáctico. Ver [DIREITOS.md](./DIREITOS.md).

## O que isto é / não é

| É | Não é |
| --- | --- |
| SQLite no servidor, sessões, papéis aluno/instrutor/admin | LMS multiusuário em `localStorage` |
| Progresso, notas, fila de correção, comprovante interno | Diploma MEC / acreditação |
| Diagnóstico do pré-teste oficial | Gráficos de desempenho inventados |
| C-COLAB verificado no backend | Execução de código enviado pelo aluno |
| Instalação privada com disco, backup e `/readyz` | Várias réplicas, SMTP, SSO, billing |

**Auth:** senha local (scrypt) + cookie HttpOnly + CSRF + sessão invalidada ao mudar a senha. Redefinição por token de uso único (30 min), emitido pelo instrutor ou pela CLI — **sem e-mail**. O auto-registo HTTP só abre com `EAD_OPEN_SIGNUP=1`. Valor `0`, ausente ou inválido fecha GET e POST, com ou sem `NODE_ENV=production`. Instrutor/admin não nascem do formulário público.

## Arranque limpo

```bash
cd curso/ead
npm ci
npm run migrate
EAD_ADMIN_EMAIL=admin@local.test EAD_ADMIN_PASSWORD='…escolha local…' npm run create-admin
HOST=127.0.0.1 PORT=3850 npm start
```

Abra `http://127.0.0.1:3850/`. A conta de aluno sai de `create-user` (papel aluno). O formulário `/registar` só aparece com `EAD_OPEN_SIGNUP=1`. Matrícula sem pagamento.

Seed **DEMONSTRAÇÃO/TESTE** (opcional, só laboratório):

```bash
EAD_SEED_DEMO=1 \
EAD_DEMO_INSTRUCTOR_PASSWORD='…' \
EAD_DEMO_ALUNO_A_PASSWORD='…' \
EAD_DEMO_ALUNO_B_PASSWORD='…' \
npm run seed
```

Essas contas aparecem com faixa **DEMONSTRAÇÃO/TESTE**. Não as trate como turma real.

Persistência: `curso/ead/data/ead.sqlite` (gitignore). Reiniciar o processo **mantém** progresso.

Preview markdown em paralelo (opcional): `npm --prefix curso/preview start` → porta 3847.

## Testes

```bash
cd curso/ead
npm test          # unidade + isolamento + fluxo HTTP
npm run a11y      # smoke de labels/skip-link; não certifica WCAG
npm run e2e       # Chrome, se existir; screenshots em /opt/cursor/artifacts
```

## Instalação privada

Procedimento, variáveis que o modo produção recusa, backup e restore: [DEPLOY-PRIVADO.md](./DEPLOY-PRIVADO.md).

Bind `0.0.0.0:$PORT`. Disco persistente em `EAD_DATA_DIR`. **Não** publicar o material CC BY-NC-ND 4.0. Esta app **não** corre em GitHub Pages e **não** traz `render.yaml` na raiz (isso publicaria o curso).

SMTP, SSO e billing continuam desligados — não há botão que finja envio.

## Dependência

Esta pasta assume a estabilização do piloto (PR de estabilização no mesmo clone): manifests, preview sanitizado, verificador C-COLAB.
