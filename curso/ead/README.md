# Sala de aula local (EaD)

Plataforma **funcional** desta pós, no mesmo repositório. Lê o pacote em `curso/` (módulos, capas, TTS, VTT, intros Grok, checkpoints de `avaliacao.md`). Não é o preview estático; não é GitHub Pages; não cobra matrícula.

Código desta pasta ≠ direitos sobre o material didáctico. Ver [DIREITOS.md](./DIREITOS.md).

## O que isto é / não é

| É | Não é |
| --- | --- |
| SQLite no servidor, sessões, papéis aluno/instrutor/admin | LMS multiusuário em `localStorage` |
| Progresso, notas, fila de correção, comprovante interno | Diploma MEC / acreditação |
| Diagnóstico do pré-teste oficial | Gráficos de desempenho inventados |
| C-COLAB verificado no backend | Execução de código enviado pelo aluno |
| Dev/teste sem conta externa | SMTP, SSO, billing, streaming premium |

**Auth:** senha local (scrypt) + cookie HttpOnly + CSRF. Sem recuperação por e-mail (SMTP desligado). Instrutor/admin **não** se registam pelo browser — só CLI.

## Arranque limpo

```bash
cd curso/ead
npm ci
npm run migrate
EAD_ADMIN_EMAIL=admin@local.test EAD_ADMIN_PASSWORD='…escolha local…' npm run create-admin
HOST=127.0.0.1 PORT=3850 npm start
```

Abra `http://127.0.0.1:3850/`. Crie a conta de aluno no browser (papel aluno). Matricule-se sem pagamento.

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

## Deploy privado

Bind `0.0.0.0:$PORT` (Render/VPS). Disco persistente no caminho `EAD_DATA_DIR`. **Não** publicar o material CC BY-NC-ND 4.0. Esta app **não** corre em GitHub Pages.

Adaptadores SMTP/SSO/billing existem só como ausência documentada — não há botão que finja envio.

## Dependência

Esta pasta assume a estabilização do piloto (PR de estabilização no mesmo clone): manifests, preview sanitizado, verificador C-COLAB.
