# Caixa — Harness engineering: consertar o agente sem trocar o modelo

Leitura opcional, ~30–45 min. Sem CA. Não entra nas 78 h de A0–A12, nas +4 h do A13, nas +4 h do A14 nem nas 240 h. Índice: [../README.md](../README.md).

## 0. Honestidade

Esta caixa **comenta** um artigo e **mede** uma simulação nossa. São coisas diferentes.

O artigo é de @0xTrackmind, «Harness Engineering: How to Fix Your Agent Without Changing the Model», 21/11/2026: <https://x.com/0xTrackmind/status/2124105677748527453> (acesso 2026-11-23). O texto da caixa é paráfrase. Não há cópia do artigo nesta pasta. Não há endosso desta trilha ao artigo, e citar não transfere licença. Registro em [../NOTICE.md](../NOTICE.md).

O exemplo do artigo (40 endpoints v1→v2, de madrugada) é **ilustrativo**. Não o medimos. No relato da fonte: no Run A (só chat) o contexto compacta no endpoint 12, a decisão de nome some, aparecem dois esquemas, o agente diz 40/40 com 11/40 de fato e os testes nunca rodam; no Run B, o mesmo modelo e o mesmo prompt dentro de um harness, 39/40 ficam verdes e 1 é escalado. Esses números ficam `ilustrativo_nao_medido`. Não os reproduzimos.

O que **nós** medimos está em [`harness/execucao/medicao.json`](./harness/execucao/medicao.json) e na seção 6. É uma simulação determinística, offline, sem API. `llm_real` = `nao_calibrado`. Screenshot de UI, typecheck e lint de um app real também são `nao_calibrado`: o sensor desta caixa é o teste do brinquedo, só isso.

Fontes que o artigo aponta, conferidas (acesso 2026-11-23):

- Anthropic, «Effective harnesses for long-running agents», 26/11/2025: <https://www.anthropic.com/research/effective-harnesses-for-long-running-agents>. A frase deles: cada sessão nova «begins with no memory of what came before». Mais adiante, um agente posterior «declare the job done». O texto descreve initializer, agente de código, `claude-progress.txt`, lista de features em JSON, commits e testes de ponta a ponta.
- Anthropic, «Harness design for long-running application development», 24/03/2026: <https://www.anthropic.com/research/harness-design-long-running-apps>. A frase deles: «Out of the box, Claude is a poor QA agent.» O desenho separa quem planeja, quem gera e quem avalia.
- OpenAI, Ryan Lopopolo, «Harness engineering: leveraging Codex in an agent-first world», 11/02/2026: <https://openai.com/index/harness-engineering/>. Lá, `AGENTS.md` é um mapa (cerca de 100 linhas), não uma enciclopédia; a documentação é o sistema de registro. Números de produto desse texto **não** entram nesta caixa como medição nossa.

## 1. A tese, no vocabulário do curso

**Harness** é o que sobra se você troca o modelo: ferramentas, arquivos, testes, permissões, logs. A falha que você atribui ao modelo muitas vezes é falha desse ambiente.

Um prompt é um pedido. Um harness é um fato. O pedido («migra as funções, e não mexe no banco») evapora quando o contexto compacta. O fato continua: o contrato está num arquivo, o teste recusa o arquivo errado, `db/` não aceita escrita.

O curso já esbarrou nisso sem usar o nome:

| Peça do curso | O que o harness teria segurado |
| --- | --- |
| [A4](../modulo-a4/README.md) | a perda só nos tokens do assistente; o collator é um fato, não um lembrete |
| [A5](../modulo-a5/README.md) | o eval publicado é `n_eval=2`; dizer «n=6» é impressão, não sensor |
| [A7](../modulo-a7/README.md) | quem verifica não é o mesmo voto que gera a resposta |
| [A12](../modulo-a12/README.md) | perplexidade de paper alheio não é número nosso; ADR em vez de colar |
| [A13](../modulo-a13/README.md) | proxy (VC, acurácia de brinquedo) não é garantia de generalização |
| [A14](../modulo-a14/README.md) | o teste congelado julga; o agente não edita a evidência |
| [M09](../../conteudo/modulo-09/aula.md) | o harness do projeto final e o portão de eval — referência conceitual, não o lab desta caixa |
| [caixa `/teamwork`](./antigravity-teamwork.md) | a suíte original, não modificada, é o yardstick |

## 2. Sete falhas, com exemplo da trilha

Cada correção abaixo existe porque uma falha real do curso (ou do brinquedo desta caixa) a paga. A ordem é a de construção: não monte as sete «por precaução» antes de ver a falha.

### (1) Tarefa errada → CONTRATO

«Melhora o assistente do sinistro» cabe num prompt e autoriza qualquer coisa: reescrever o JSONL do M09, «limpar» o eval, mudar a máscara. O contrato nomeia `goal`, `output`, `scope`, `never`, `done_when`. Modelo: [`harness/templates/CONTRACT.md`](./harness/templates/CONTRACT.md).

### (2) Ignora regras → mapa curto

Colar o guia de estilo inteiro no prompt foi o caminho de o A5 aplicar perda no turno do usuário: a regra importante afoga. `AGENTS.md` tem uma dúzia de linhas e aponta os docs. Modelo: [`harness/templates/AGENTS.md`](./harness/templates/AGENTS.md). Os docs desta caixa cabem numa página cada: [arquitetura](./harness/docs/arquitetura.md), [regras da API](./harness/docs/regras-api.md), [testes](./harness/docs/testes.md).

### (3) Ferramenta errada → ferramenta estreita, falha barulhenta

«Busca no repositório» devolve o JSONL do M09, o lab do A14 e um comentário de 2024. A ferramenta desta caixa só conhece as 12 funções de [`harness/brinquedo/funcoes.py`](./harness/brinquedo/funcoes.py). Id inexistente ou pasta `db/` não vira um resultado vazio educado: vira erro com nome (`ferramenta_vazia`, `muro_db`).

### (4) Esquece decisões → estado em arquivo

A janela compacta. A decisão «campos v2 em snake_case; códigos de erro v1 ficam» precisa viver em [`PROGRESS.md`](./harness/templates/PROGRESS.md): `done`, `current`, `decisions`, `dead ends`, `blocked`. Um commit por etapa. No modo A da simulação a decisão sai do contexto e o agente regrava funções já feitas com outro esquema. No modo B a decisão está no arquivo, fora da janela.

### (5) «Pronto» sem estar → SENSORES

«Os testes devem passar», uma perplexidade inventada (A12), ou «o eval do A5 tem n=6». Pergunta de sensor: **a evidência poderia ter voltado vermelha?** Se não, é a impressão de quem construiu. Quem avalia fica separado de quem escreve — o A7, o A14 e o texto da Anthropic de março de 2026 dizem a mesma coisa em escalas diferentes. Aqui o sensor é o predicado `("rotas", "snake")`. Screenshot, typecheck e lint de UI ficam `nao_calibrado`.

### (6) Repete o mesmo conserto → SAÍDAS

Verde → próximo. O mesmo erro duas vezes → parar, registrar, escalar. Orçamento estourado → parar. Modelo: [`harness/templates/EXIT.md`](./harness/templates/EXIT.md). Sem saída, o agente gasta a noite no mesmo `muro_db`.

### (7) Mexe no que não deve → MUROS

Editar `db/` ou o teste congelado para o número ficar verde (a caixa `/teamwork` e o A14). Permissão: `db/` é leitura. Na simulação a tentativa de escrever em `db/` conta; o arquivo não muda.

## 3. Remendar a rodada ou consertar o harness

| O que aconteceu | Remendo da rodada | Conserto do harness |
| --- | --- | --- |
| Esqueceu o esquema de nome | colar a regra de novo no chat | `PROGRESS.md` + commit da decisão |
| Disse 12/12 com 4 prontas | pedir «confira, por favor» | o relatório só pode repetir o sensor |
| Escreveu em `db/` | apagar o arquivo à mão | `db/` read-only; a escrita falha alto |
| Ferramenta voltou vazia | repetir o prompt | ferramenta estreita; segundo erro igual escala |
| Inventou streaming no export | aceitar o diff | `never` no contrato; id 11 vai para `blocked` |

O remendo conserta aquela madrugada. O harness conserta a próxima, com outro modelo.

## 4. Era o modelo?

Dê a um engenheiro humano exatamente o que o agente tinha. No modo A, depois da compactação, isso é o resumo «alguns endpoints mexidos», sem a lista do que já ficou verde e sem a regra de nome. Um humano com só isso também erra o esquema. A falha não era o modelo.

Se o humano, com o contrato, o `PROGRESS.md`, o teste e a pasta `db/` bloqueada, termina a migração, o modelo que falhou no chat estava sem os fatos. Trocar de modelo não cria esses fatos.

## 5. Construir em ordem

Cada peça paga uma falha que você já viu. Não antecipe.

| Ordem | Peça | Falha que ela paga | Nesta caixa |
| --- | --- | --- | --- |
| H0 | CONTRATO | tarefa errada | template + modo B |
| H1 | AGENTS.md | regra ignorada | template; não entra no RNG |
| H2 | ferramenta estreita | ferramenta errada | erro `ferramenta_vazia` no modo B |
| H3 | PROGRESS.md | decisão esquecida | modo B não troca o esquema |
| H4 | sensor | «pronto» sem estar | teste é o portão do modo B |
| H5 | EXIT | mesmo conserto em loop | teto 2; erro repetido escala |
| H6 | muro | escrita fora do escopo | `db/` tentado, não aplicado |

H1 não muda o número da simulação. O mapa existe para o leitor; o script não «lê» markdown. Dizer que o mapa reduziu erro seria `nao_calibrado`.

## 6. Exercício (offline, ~15 min do tempo da caixa)

Simulação didática. Não é medição de LLM. Seeds `0..19`. Desvio = amostral (`statistics.stdev`, n−1). Comando, na raiz da trilha:

```bash
cd curso/trilha-avancada
python caixas/harness/lab/simular.py
```

O script reescreve [`harness/execucao/medicao.json`](./harness/execucao/medicao.json). Rodar de novo com as mesmas seeds produz o mesmo JSON. Notas da execução: [`harness/execucao/run-vm.md`](./harness/execucao/run-vm.md).

Doze funções, não quarenta. Janela do modo A = 6. Probabilidade de tentar `db/` = 0,22. Probabilidade de ferramenta vazia no modo B = 0,18. O id 11 (`export_claims`) no modo B é sempre escalado: a decisão de streaming não está no contrato.

Medição desta VM (20 seeds), também no JSON:

| | Modo A (só chat) | Modo B (harness) |
| --- | --- | --- |
| Relatado (média ± desvio) | `12.0` ± `0.0` | `10.1` ± `0.8522` |
| Concluídas de verdade (média ± desvio) | `3.2` ± `0.7678` | `10.1` ± `0.8522` |
| Violações de escopo aplicadas | `3.3` ± `1.2183` | `0.0` ± `0.0` |
| Violações de escopo tentadas | no A, tentou = aplicou | `2.6` ± `1.729` |
| Tentativas desperdiçadas | `9.2` ± `1.0052` | `4.8` ± `2.1423` |
| Escalados | `0` em toda seed (não há saída) | `1.9` ± `0.8522` |
| Testes rodados | não | sim |

Seed 0, para ler o traço: no A, relata 12, conclui 4, aplica 4 escritas em `db/`, regrava `postClaim` e `getPolicy` com o outro esquema, teste não roda. No B, relata 11, conclui 11, nenhuma escrita em `db/` aplicada, 1 escalado (o export).

O modo A mente por construção: `relatado` é `N` e o teste não roda. O modo B só relata o que o sensor contou (`relatado == concluidas`) e a escrita em `db/` não gruda. A média de concluídas do B fica acima da do A nestas seeds. Isso **não** é o 11/40 nem o 39/40 do artigo.

Perguntas (papel, sem API):

1. No modo A, qual número é impressão e qual é sensor?
2. Um humano que só recebeu «alguns endpoints mexidos» saberia que o esquema é `snake_case`?
3. Qual falha o muro segura que o remendo «apaga o arquivo» não segura na próxima rodada?

Resposta curta da (1), para conferir: impressão = 12; sensor = a coluna `concluidas` (média `3.2`).
