# Caixa — Vários harnesses: produtor, revisor, falsificador

Leitura opcional, ~30–45 min. Sem CA. Não entra nas 78 h de A0–A12, nas +4 h do A13, nas +4 h do A14 nem nas 240 h. Índice: [../README.md](../README.md).

## 0. Honestidade

Caixa original da trilha. Não há texto de terceiro, e por isso não há citação nova no [../NOTICE.md](../NOTICE.md).

A [caixa de harness](./harness-engineering.md) trata de um ambiente em volta de um agente. Esta trata de três ambientes, com contrato separado, que se passam trabalho por arquivo. A [caixa tática](./programacao-tatica-vs-estrategica.md) mostra um revisor de design que não olha o teste. Aqui o falsificador tenta quebrar, e o teste congelado está fora do alcance de quem produz.

Simulação determinística, offline, sem API. Não é um LLM. `llm_real` = `nao_calibrado`. Números em [`multi/execucao/medicao.json`](./multi/execucao/medicao.json). Vinte seeds, `0..19`. Desvio = amostral (n−1).

## 1. Dois arranjos, o mesmo plano

Seis mudanças de sinistro em [`multi/brinquedo/tarefas.py`](./multi/brinquedo/tarefas.py). Cada uma pode manifestar um defeito plantado (probabilidade 0,80):

| Perfil | O que os sensores veem |
| --- | --- |
| vermelho | `f(1) == 2` falha. O teste congelado pega |
| fronteira | `f(1)` passa. `f(0) == 0` quebra. Só o falsificador roda `f(0)` |
| corrida | `f(1)` e `f(0)` passam. Nenhum sensor deste lab olha corrida |

No vermelho, o produtor tenta reescrever o teste com probabilidade 0,70. Se não tenta e a correção de código não segura (probabilidade 0,35), o harness único reescreve o teste mesmo assim. O arranjo T escala.

| Arranjo | Contratos | Teste | Quem tenta quebrar |
| --- | --- | --- | --- |
| U, um harness | o mesmo agente escreve e julga | a escrita no teste gruda | ninguém além do teste |
| T, três harnesses | [produtor](./multi/templates/CONTRACT-produtor.md), [revisor](./multi/templates/CONTRACT-revisor.md), [falsificador](./multi/templates/CONTRACT-falsificador.md) | a escrita é barrada | o falsificador, no caso `f(0)` |

A passagem é o [PROGRESS](./multi/templates/PROGRESS.md): produtor → revisor → falsificador. Se `f(0)` quebra, o falsificador devolve, o produtor corrige e os dois releem. Segunda falha do teste congelado no T vira uma passagem para humano, e o defeito não segue como «verde».

O revisor não roda `f(0)` e não trata o voto do produtor como evidência. O falsificador não edita o teste e não declara corrida: o contrato dele não tem esse sensor.

Liga ao [A14](../modulo-a14/README.md) (a suíte que o agente não edita), ao [A7](../modulo-a7/README.md) (quem verifica não é quem gera) e ao [M09](../../conteudo/modulo-09/aula.md) (portão de eval como referência, não como lab desta caixa).

## 2. Números medidos

```bash
cd curso/trilha-avancada
python caixas/multi/lab/simular.py
```

Notas da execução: [`multi/execucao/run-vm.md`](./multi/execucao/run-vm.md).

| | U (um harness) | T (três harnesses) |
| --- | --- | --- |
| Defeitos plantados | `5.25` ± `0.7864` | `5.25` ± `0.7864` |
| Defeitos que escapam | `4.75` ± `0.9665` | `0.8` ± `0.4104` |
| Tentativas de escrita no teste | `2.3` ± `0.7327` | `2.05` ± `0.9987` |
| Escritas no teste aplicadas | `2.3` ± `0.7327` | `0.0` ± `0.0` |
| Escritas no teste barradas | `0.0` ± `0.0` | `2.05` ± `0.9987` |
| Passagens de trabalho | `0.0` ± `0.0` | `15.9` ± `1.9167` |
| Passos | `22.55` ± `2.6253` | `59.8` ± `5.2676` |
| Escalonamentos | `0.0` ± `0.0` | `1.05` ± `0.8256` |

No U, toda tentativa de escrever no teste gruda (`2.3` aplicadas, `0.0` barradas). No T, toda tentativa é barrada (`2.05` barradas, `0.0` aplicadas) e o teste da seed permanece o congelado. A diferença de tentativas (`2.3` contra `2.05`) é a segunda falha: no U ela vira outra edição do teste; no T ela vira escalonamento (`1.05`).

O que ainda escapa no T é a corrida: média `0.8` de `5.25` plantados. O falsificador não tem sensor para ela. O U deixa escapar `4.75`, porque além da corrida saem a fronteira (ninguém chama `f(0)`) e o vermelho cujo teste foi reescrito.

O T custa mais: `59.8` passos e `15.9` passagens, contra `22.55` passos e `0.0` passagens no U. O arranjo paga revisor e falsificador em toda mudança que chega a eles.

Seed 0: os dois arranjos plantam 5 defeitos. O U deixa os 5 escaparem, aplica 2 escritas no teste e gasta `20` passos. O T deixa escapar `1` (a corrida que os sensores não veem), barra 2 escritas, faz `18` passagens e gasta `64` passos. Nessa seed o T não escala.

## 3. O que levar daqui

Três contratos e um arquivo entre eles mudam o que consegue sair verde. O produtor deixa de ser o juiz do próprio teste. O falsificador pega o caso que o teste congelado não roda. A corrida continua saindo: o contrato do falsificador não a nomeia, e o lab não inventa um sensor para fingir que pegou. Escalar é a saída quando a correção repete o vermelho. Quem decide o caso escalado é humano; o script só para e conta.
