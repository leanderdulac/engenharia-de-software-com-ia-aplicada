# Caixa — Programação tática e programação estratégica

Leitura opcional, ~30–45 min. Sem CA. Não entra nas 78 h de A0–A12, nas +4 h do A13, nas +4 h do A14 nem nas 240 h. Índice: [../README.md](../README.md).

## 0. Honestidade

A tese é do autor do curso. Não há texto de terceiro nesta caixa, e por isso não há citação nova no [../NOTICE.md](../NOTICE.md).

Modelos vão bem na programação tática: um objetivo fechado, um código que passa. Vão pior na programação estratégica: escolher agora pensando no código que ainda vai ser escrito. O loop de verificação — o teste — melhora a parte tática. Não melhora a estratégica. Pode piorá-la, porque o agente aceita um atalho que deixa o teste verde. O curso chama esse efeito de lei de Goodhart: a métrica, quando vira a única meta, deixa de descrever a saúde do código.

O que esta caixa mede é uma simulação determinística, offline, sem API. Não é um LLM. `llm_real` = `nao_calibrado`. Os números abaixo saem de [`tatica/execucao/medicao.json`](./tatica/execucao/medicao.json). Vinte seeds, `0..19`. Desvio = amostral (n−1).

## 1. Trazer a estratégia para dentro do loop

Três peças, cada uma com um furo declarado. Templates: [ADR-001](./tatica/templates/ADR-001.md), [regras](./tatica/templates/REGRAS.md), [revisor](./tatica/templates/REVISOR-DESIGN.md), [métricas](./tatica/templates/METRICAS-DEBITO.md). O código das oito features está em [`tatica/brinquedo/catalogo.py`](./tatica/brinquedo/catalogo.py).

**Regras de arquitetura verificáveis.** `api.py` não importa `persistencia.py`. Dependência nova (`requests`) sem ADR é recusada. Função com mais de 4 statements no corpo estoura o orçamento do diff. A regra não vê cópia de corpo, nem `legacy`, nem `streaming`. Quando ela dispara, o agente do modo B grava uma cópia curta. A cópia passa no teste. A regra fica quieta.

**Revisor de design separado.** Lê o diff e o ADR. A função é `revisor_design(tipo, trecho)`. Não recebe o booleano do teste. Recusa lista copiada, corpo copiado de `gravar` e parâmetro `legacy`. No `streaming`, não decide: devolve `escalar`.

**Métrica de débito ao longo da seed.** Cada feature paga `1` passo a mais por violação já aceita. O custo da feature seguinte é `4 + violações`, com `4` = custo limpo. Duplicação é a contagem de funções em `api.py` que copiam a lista do registro ou o corpo de `gravar`.

Decidir qual débito aceitar continua humano. O modo C escala o `streaming` (média `0.65`) e não o grava. O script não tem um ramo «aceitar o débito».

O curso já separa quem mede de quem escreve: o [A7](../modulo-a7/README.md) separa o voto de quem verifica, o [A12](../modulo-a12/README.md) pede ADR em vez de número emprestado, o [A14](../modulo-a14/README.md) deixa o teste congelado julgar. A [caixa de harness](./harness-engineering.md) é o ambiente em volta do modelo. Esta caixa olha o que esse ambiente otimiza.

## 2. Três modos, o mesmo plano

Oito features. Em cada seed o agente tenta atalho com probabilidade 0,75. Com probabilidade 0,20 o atalho é um bug e o teste barra. Esse sorteio é o mesmo nos três modos.

| Modo | O que entra no código |
| --- | --- |
| A | teste congelado. Atalho verde entra |
| B | teste + regra mecânica. Se a regra dispara, entra a cópia |
| C | B + revisor. Cópia e `legacy` não entram. `streaming` escala |

O teste verde não muda: os três modos caem na versão limpa quando o atalho não entra. A nota tática fica igual. A nota estratégica, não.

## 3. Números medidos

Comando, na raiz da trilha:

```bash
cd curso/trilha-avancada
python caixas/tatica/lab/simular.py
```

Notas da execução: [`tatica/execucao/run-vm.md`](./tatica/execucao/run-vm.md).

| | A (só testes) | B (testes + regra) | C (B + revisor) |
| --- | --- | --- | --- |
| Entregues com teste verde | `8.0` ± `0.0` | `8.0` ± `0.0` | `8.0` ± `0.0` |
| Violações acumuladas | `5.4` ± `1.2312` | `5.4` ± `1.2312` | `0.0` ± `0.0` |
| Duplicação | `1.2` ± `0.6959` | `3.15` ± `1.1367` | `0.0` ± `0.0` |
| Custo da feature seguinte | `9.4` ± `1.2312` | `9.4` ± `1.2312` | `4.0` ± `0.0` |
| Passos desta leva | `43.4` ± `5.7436` | `46.65` ± `7.5969` | `35.85` ± `1.7554` |
| Atalhos tentados | `6.35` ± `1.0894` | `6.35` ± `1.0894` | `6.35` ± `1.0894` |
| Atalhos aceitos | `5.4` ± `1.2312` | `5.4` ± `1.2312` | `0.0` ± `0.0` |
| Barrados pelo teste | `0.95` ± `0.8256` | `0.95` ± `0.8256` | `0.95` ± `0.8256` |
| Disparos da regra | `0.0` ± `0.0` | `1.95` ± `0.887` | `1.95` ± `0.887` |
| Recusas do revisor | `0.0` ± `0.0` | `0.0` ± `0.0` | `5.4` ± `1.2312` |
| Escalonados (`streaming`) | `0.0` ± `0.0` | `0.0` ± `0.0` | `0.65` ± `0.4894` |

O modo B dispara a regra `1.95` vezes por seed e mesmo assim aceita `5.4` atalhos, os mesmos do A. A violação e o custo da feature seguinte ficam iguais (`5.4` e `9.4`). A duplicação sobe de `1.2` para `3.15`. Os passos sobem de `43.4` para `46.65`. A regra, sozinha, não segurou o débito: o agente trocou o atalho barrado por uma cópia.

O modo C aceita `0.0` atalhos. Violação, duplicação e custo seguinte ficam no piso (`0.0`, `0.0` e `4.0`, desvio `0.0`): o revisor deste brinquedo é um predicado sobre o diff, completo para cópia e `legacy`, e o `streaming` sai por `escalar`. Isso não é a taxa de acerto de um revisor LLM. Essa taxa está `nao_calibrado`.

Os passos do C (`35.85`) ficam abaixo dos do A (`43.4`) porque a fórmula cobra a multa do débito dentro da própria leva. O atalho barato (`2` em vez de `4`) deixa de ser barato depois que a multa acumula. Fora desta fórmula, o custo de um revisor humano está `nao_calibrado`.

Seed 0, para ler o traço: o A entra com 5 violações (1 complexidade, 2 duplicações, 1 `legacy`, 1 `streaming`) e a feature seguinte custa `9`. O B dispara a regra 1 vez, a complexidade vira cópia (duplicação `3`) e a feature seguinte continua em `9`. O C recusa as 5, escala 1 e a feature seguinte custa `4`.

## 4. O que levar daqui

O teste iguala a entrega tática nos três modos: `8.0` ± `0.0`. Estratégia entra no loop quando a regra, o revisor e a multa olham o diff, não só o verde. A regra sem revisor, neste lab, aumenta a duplicação. O revisor sem um humano no `streaming` também não «aceita débito com sabedoria»: ele se recusa a decidir. Essa decisão fica com quem lê o ADR.
