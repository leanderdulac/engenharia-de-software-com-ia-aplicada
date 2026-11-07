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
| m02-langchain-intro | **PASS** exit=0 (`npm test` 3/3, sem `.env`) |
| m09-grpo-math | **PASS** exit=0 (10 testes de matemática offline; rollout Ollama falhou sem runtime e o script ainda sai 0) |
| c052-a11y-static | **PASS** exit=0 (templates Pix; **não** é WCAG) |
| m01-exemplo-11-header | **SKIP** inspect_only |
| m06-nexus | **SKIP** blocked_secrets |
| m08-react-ollama | **SKIP** blocked_runtime |
| m09-lora-mlx | **SKIP** blocked_gpu |
| m09-vertex | **SKIP** blocked_secrets |
| companion-rag-cpu | **SKIP** blocked_model_download |
| m04-opspilot | **SKIP** blocked_secrets |
| m02-openrouter-labs | **SKIP** blocked_secrets |
| m03-mcp | **SKIP** blocked_docker |
| m05-bragbot | **SKIP** blocked_secrets |

Labs **não** foram removidos para o smoke passar.

## Rodada 2 — fontes oficiais (revisão documental, não execução)

Conferido em 7 nov. 2026. **Não** baixámos modelos. **Não** abrimos o Inspector. **Não** é parecer jurídico.

| Afirmação | Fonte | O que **não** fizemos |
| --- | --- | --- |
| `gemma4:e2b` existe; tamanho 4,6–7,5 GB | [ollama.com/library/gemma4](https://ollama.com/library/gemma4) | `ollama pull` |
| `nomic-embed-text` 274 MB | [ollama.com/library/nomic-embed-text](https://ollama.com/library/nomic-embed-text) | download |
| Inspector: `npx @modelcontextprotocol/inspector`; UI `CLIENT_PORT` 6274 | [docs](https://modelcontextprotocol.io/docs/tools/inspector); [env](https://github.com/modelcontextprotocol/inspector/blob/main/docs/environment-variables.md) | abrir UI |
| Site MCP: Node ≥22.19.0. Pacote 2.14.0 `engines`: `^22.23.4 \|\| ^24.22.1 \|\| >=26.12.1` | mesmo docs; [package.json](https://github.com/modelcontextprotocol/inspector/blob/main/package.json) | instalar o Inspector |
| Dado pessoal sensível inclui saúde | [LGPD Lei 13.709/2018 Art. 5º II](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) | parecer / DPA real |
| Supervised fine-tuning Gemini cotado em USD / 1.000 tokens | [pricing Google Cloud](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing) | job Vertex |
| GRPO demo: math offline 10/10; papers DeepSeekMath / R1 | arXiv:2402.03300, 2501.12948; `node grpo-verifiable-reward-demo.js` | treino de pesos / rollout Ollama |

e2e Chrome (após cleanup `rmSync` com retry): home, hash M01, aula+reload, Apache isolado. Residual `/tmp` do perfil Chrome **não** falha o teste.

C05.2: `node curso/piloto/check-a11y-c052.mjs` — lang, skip-link, labels, Escape no modal, `aria-hidden` em ícones. Angular **não** compilado; CFP **não** executado.

## Rodada 3 — execução real (gargalo técnico)

Instalações nesta VM (gratuitas, sem contas pagas, bind local):

| Runtime | Versão / evidência |
| --- | --- |
| Node trilha | v22.23.4 (`/exec-daemon/node`) |
| Node Inspector/M03 | v24.22.1 (`~/.nvm/versions/node/v24.22.1`) |
| Docker | 29.1.3; `dockerd` arrancado à mão (sem systemd). `docker` sem grupo → `permission denied` no sock; `sudo docker` OK. `hello-world` OK. |
| Mongo | `mongo:8` `piloto-mongo` em `127.0.0.1:27017` (root/example) |
| Verdaccio | `verdaccio/verdaccio:6` `piloto-verdaccio` `127.0.0.1:4873` HTTP 200 |
| Ollama | 0.40.15; `nomic-embed-text` (768 dims) + `tinyllama` handshake `num_predict:8`. **Não** puxámos `gemma4:e2b` (~5 GB+) |
| Chrome | e2e preview PASS |

Comandos e resultados (reexecução após correções):

```
npm --prefix curso/preview test          # 21/21
npm --prefix curso/preview run check     # fail=0 warn=0 ok=13
npm --prefix curso/preview run e2e       # PASS
node curso/piloto/check-a11y-c052.mjs    # PASS (não WCAG)
node curso/piloto/check-contratos.mjs    # PASS (TESTE LOCAL ≠ integração)
CipherSuite npm test (Node 22 e 24)      # 4/4; EBADENGINE 24.22.1 vs engines v24.14.0 (aviso)
Inspector CLI tools/list                 # encrypt_message / decrypt_message
customers-mcp npm test (API :9999)       # 6/6
CRUD npm test (Mongo)                    # 9/9
Pix ng build + vitest                    # build OK; 4/4 (specs corrigidos)
nx build frontend + nx build api         # OK (lockfile CFP sincronizado)
RouteWise submodule npm test             # 12/12 em 7c52d76
nomic embed                              # nomic_dims 768
tinyllama generate                       # tinyllama_handshake_ok
GRPO math                                # 10/10; rollout gemma4 404 (modelo não puxado)
```

Python `danger-config-routewise.py` **não** está no submódulo; **não** foi executado.

Daemon Docker: não contornámos cgroup/seccomp. `usermod -aG docker` não renovou o grupo nesta sessão; smoke usa `sudo -n docker info`.

## O que isto não prova

- Integração OpenRouter / Groq / Gemini / Vertex (contratos herméticos só).
- GPU / MLX / LoRA `adapters.safetensors` / treino GRPO de pesos / paridade `gemma4:e2b`.
- UI Inspector na porta 6274 (handshake foi CLI).
- Python Danger da disciplina; qualidade TTS/vídeo (evidência = ficheiros no disco).
- Aprendizagem de alunos ou autorização jurídica (fora do gargalo técnico desta rodada).
- Preview remoto persistente (Pages não ligado).
