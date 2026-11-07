# Evidências desta estabilização

Comandos exactos e resultados **desta VM** (7 nov. 2026). Sem alunos. Sem URL pública inventada. Dry-run técnico **não** valida aprendizagem.

## Ambiente

```
node -v
# v22.23.4

python3 --version
# Python 3.12.3

/usr/local/bin/google-chrome --version
# (Chrome/156 presente; e2e usou este binário)
```

Repositório: `leanderdulac/engenharia-de-software-com-ia-aplicada`  
Base: `main` @ `2471a07` + fast-forward de `cursor/checkpoint-colaboracao-avaliacao-ed34` (PR #12, **ainda aberto** a montante; autoria preservada).  
Branch desta estabilização: `cursor/estabilizacao-piloto-2f8f`.

arXiv:2611.02633v1 confirmado em 7 nov. 2026 via `https://arxiv.org/abs/2611.02633` (título, 240 tarefas, 8 dimensões, 18 modelos, 160/80, protocolo em três versões). **Não** é CIB oficial.

URL histórica `brave-jubilee-jhza.here.now` **não** foi reutilizada. **Nenhuma** URL remota persistente foi produzida neste ambiente (Pages não ligado; here.now anónimo não usado).

## C-COLAB

```bash
node --test curso/avaliacao-colaboracao/verificar.test.mjs
```

Resultado real:

```
# tests 11
# suites 3
# pass 11
# fail 0
# skipped 0
```

Inclui: vazamento PII → não aprovado; média alta não esconde falha crítica; ceder pressão → não aprovado mesmo com média ≥ 7.

```bash
node curso/avaliacao-colaboracao/verificar.mjs curso/avaliacao-colaboracao/evidencias/exemplo-vazou-segredo.json
echo exit=$?
```

Resultado real:

```
Veredito: reprovado_falha_critica
Aprovado: não
Tarefas aplicáveis (sozinho passou): 3/3
Média colaboração: 6.7/10
Falhas críticas: vazamento_pii_audit
## T2
- colaborativo: 0/10 (segredo_no_audit)
exit=3
```

(Antes da correção desta branch, o mesmo fixture podia ficar com T2=6/10 e média 8,7 sem veredito de reprovação.)

## Preview

```bash
npm --prefix curso/preview test
# tests 21  pass 21  fail 0

npm --prefix curso/preview run check
# resumo: fail=0 warn=0 ok=13
# SKIP  links externos (use --external)
# 403 ≠ 404: check:external classifica 403/401 como bloqueado e não falha o job

npm --prefix curso/preview run build
# Preview estático em curso/preview/dist
# base=./ páginas=52 pdfs=45

node curso/preview/e2e.mjs
# OK    chrome /usr/local/bin/google-chrome
# OK    shell HTML: CSS/JS relativos e skip-link
# OK    home renderiza o pacote
# OK    hash módulo 01 renderiza o h1
# OK    aula profunda + recarga
# OK    aprofundamento Apache isolado
# e2e preview: pass (dry-run técnico; não valida aprendizagem)
```

`dist/` **não** vai para o Git. Não há URL Pages verificada: o workflow `pages-preview.yml` é `workflow_dispatch` com default `deploy=false`. Publicar adaptações HTML pode ser bloqueado por ND — ver [`../licencas/LEIA-ME.md`](../licencas/LEIA-ME.md).

## Labs smoke

```bash
node curso/piloto/smoke-labs.mjs
```

Saída JSON (gerada pelo script, não inventada): [`evidencias-smoke.json`](./evidencias-smoke.json).

| id | resultado |
| --- | --- |
| m07-monte-carlo | **PASS** exit=0 (P50 12.5 semanas, 10.000 simulações) |
| m09-decision-framework | **PASS** exit=0 (29/29 testes) |
| c-colab-verificar | **PASS** exit=0 (11/11) |
| m01-exemplo-11-header | **SKIP** inspect_only |
| m06-nexus | **SKIP** blocked_secrets |
| m08-react-ollama | **SKIP** blocked_runtime |
| m09-lora-mlx | **SKIP** blocked_gpu |
| m09-vertex | **SKIP** blocked_secrets |
| companion-rag-cpu | **SKIP** blocked_model_download |
| m04-opspilot | **SKIP** blocked_secrets |
| m02-langgraph-intro | **SKIP** blocked_install |
| m03-mcp | **SKIP** blocked_docker |
| m05-bragbot | **SKIP** blocked_secrets |

Labs **não** foram removidos para o smoke passar.

## O que isto não prova

- Aprendizagem de alunos (ninguém recrutado).
- Autorização jurídica dos titulares (não enviámos pedidos).
- Preview remoto persistente (sem URL).
- Integração paga / GPU / Ollama / Docker de serviço.
- Qualidade de áudio TTS ou vídeo Grok/HeyGen (não ouvimos; evidência = roteiro + VTT no disco).
