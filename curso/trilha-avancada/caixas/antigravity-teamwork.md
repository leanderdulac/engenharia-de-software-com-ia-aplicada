# Caixa — Antigravity `/teamwork`: falsificador objetivo, não “o agente disse que passou”

Leitura **opcional**, ~30 min. Sem CA. Não entra nas 78 h, nas +4 h do A13 nem nas 240 h. Índice: [`../README.md`](../README.md).

Isto **não** é um tutorial do produto Antigravity, nem um lab a reproduzir. É um estudo de caso para ligar um anúncio de 13/11/2026 a três ideias que a trilha já treinou: verificação (A7), medição real no ADR (A12) e a diferença entre *proxy* e *garantia* (A13).

---

## 0. Honestidade (leia isto primeiro)

Todos os números desta caixa são **alegações do próprio Google**, publicadas no blog de Research e no post de Vahab Mirrokni. **Ninguém nesta trilha replicou** Zircon, libgav1, JAXBench, Lean 4 nem TPU. **Não há endosso** do produto, dos modelos Gemini 4 nem da metodologia. Se um agente no seu projeto “passa no teste”, a pergunta continua a do A12: *qual suíte, em qual hardware, com o teste original intacto?*

Fontes (acesso 2026-11-14):

- Vahab Mirrokni, *Advancing science & engineering with Antigravity’s /teamwork*, Google Research, **13/11/2026**. <https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/>
- Post de Mirrokni, **13/11/2026** 21:15 UTC. <https://x.com/mirrokni/status/2121351383236436247>

NOTICE: [`../NOTICE.md`](../NOTICE.md).

---

## 1. Arquitetura alegada (três peças)

O blog motiva `/teamwork` com dois limites de LLM de contexto longo: a geração é instável (uma tentativa não basta) e a atenção se espalha em tarefas de dias. A resposta descrita **não** é “um agente maior”. São três construtos.

**Exploração paralela + falsificadores objetivos.** Vários candidatos correm; um verificador *externo ao modelo* decide quem sobrevive. Exemplos citados pelo Google: checador Lean 4, **suítes de teste de software não modificadas**, simuladores de execução, busca na web, contadores de hardware. O ponto pedagógico não é a lista: é que o veredicto não sai do mesmo decoder que produziu o patch.

**Contexto particionado por construção.** Cada agente especializado recebe só os arquivos e as ferramentas daquele passo. Coordenadores passam a tarefa a sucessor *fresco*. Críticos e auditores revisam **em contexto limpo**, sem o raciocínio do produtor. Isso ataca o truque clássico: o modelo que “explica” o próprio erro até parecer certo.

**Padrões declarativos.** O fluxo é um padrão em linguagem natural, não um grafo escondido no prompt. O blog empacota um deles como `/boost`: loop **sequencial** resolver-e-verificar, refinado a partir de trajetórias anteriores — e diz que código fortemente acoplado piorava quando fatiado em paralelo. `/teamwork` roteia o prompt ao padrão; `/boost` é o caso “implementa, verifica, revisa”.

Nada disto foi medido nesta CPU. Leia como *desenho de harness*, não como resultado reproduzido.

---

## 2. Caso de engenharia: Zircon e libgav1

O blog afirma uma campanha de duas semanas (modelo Argon) sobre o microkernel **Zircon**: a partir de um porto inicial de ~25%, o restante do C++ teria virado cerca de **800 mil linhas** de Rust *safe*, passando os testes unitários do kernel e **bootando em hardware arm64**.

Sobre **libgav1** (decoder AV1 da Google): reescrita C++ → cerca de **170 mil linhas** de Rust, com **paridade bit a bit** numa suíte de conformidade larga. No começo o porto teria ficado ~**4× mais lento** que o C++ original. Depois de dar ao `/teamwork` acesso a **profilers** e a um mandato de velocidade em clips de amostra, o Rust teria ficado **20–30% mais rápido** que o C++ e o assembly feito à mão, em x86_64 e ARM.

**Lição que a trilha extrai — independente de você acreditar nos números.** Migração grande falha quando o agente (1) inventa stub da dependência que ainda não compilou ou (2) **edita o teste** para o porto quebrado “passar”. O padrão descrito agenda cada módulo **só depois** das dependências compilarem, e liga a folha contra a **suíte original, não modificada**. É o mesmo instinto do harness do M09 (eval em hold-out que o treino não reescreve) e do A12 (não colar ppl de outra máquina no ADR). Aqui o “hold-out” é o teste que o agente **não pode tocar**.

O post no X resume os mesmos 800k / 170k / 20–30% (Mirrokni, 13/11/2026). Continua alegação de primeira parte.

---

## 3. DuoDiscover: proxy rápido ≠ hardware

Avaliar um kernel JAX/Pallas no TPU, segundo o blog, leva **7–32 min**. Isso mata a busca: poucos candidatos. O padrão **DuoDiscover** teria posto quatro agentes em paralelo para achar gargalos e construir avaliadores-proxy de **23 s**, apelidados *yardsticks*. A ordem que o proxy produz é **validada de tempos em tempos** contra a corrida completa no hardware, com correlação de postos de **Kendall**. Número de capa: **4,09×** de média geométrica em **17** kernels JAXBench (e, no mesmo parágrafo, 2,99× em 7 kernels Pallas do vLLM TPU-Inference — mesma ressalva: não medido aqui).

**Lição.** Proxy só vale se a correlação com o ouro **é monitorada**. No dia em que Kendall cai, o yardstick virou o teste que o agente otimiza — o irmão industrial do rótulo aleatório do A13 e do “certo pelo motivo errado” do A7. Velocidade do proxy sem o gráfico de correlação é marketing.

---

## 4. Onde isso senta na trilha (e no M09, sem editá-lo)

| Peça da trilha | O que você já fez | O que a caixa acrescenta |
| --- | --- | --- |
| [A7](../modulo-a7/README.md) | Self-consistency (voto) e verificador de *resultado* vs. de *passo*; CoT pode piorar no 135M | Voto entre amostras do **mesmo** modelo ≠ falsificador **objetivo** (Lean, teste intacto, timer). O A7 mostrou o primeiro; o anúncio descreve o segundo. |
| [A12](../modulo-a12/README.md) | ADR com duas técnicas **medidas nesta CPU**; recusar INT8 porque o ppl piorou | “Passa no kernel e boota arm64” é o formato de evidência que o ADR pede. Sem o JSON **seu**, o A12 zera. Sem a suíte **original**, a migração também. |
| [A13](../modulo-a13/README.md) | Bound VC vácuo; Zhang: treino 1,00 com y aleatório | Yardstick de 23 s é um *proxy de capacidade/desempenho*. Como o `h_proxy` do LoRA, só informa se você **calibra** contra o ouro. Kendall é a calibração; VC não é. |
| M09 (não editar) | Harness, eval gate, “não treinar” como decisão | A suíte intocada é o eval gate aplicado a **código**, não a JSON de sinistro. Apontamos o módulo; **não** copiamos o harness nem o ADR do tronco. |

A9 (recompensa verificável) é primo: r tem de vir de um oráculo que o modelo não reescreve. Esta caixa não pede A9.

---

## 5. Exercício (~15 min de papel)

Escolha **uma** migração real do *seu* projeto (não do JSONL do M09): por exemplo Python 3.10→3.12, JS→TypeScript, collator que misturava prompt, ou “trocar o decoder AV1” numa lib pequena que você controla.

Desenhe um harness de uma página com três caixas:

1. **Produtor** — o que pode editar (código da folha, nunca o teste).
2. **Falsificador objetivo** — comando concreto (`pytest -q` na suíte *congelada*, `cargo test` do upstream, bit-exact vs. fixture versionada, timer de hardware). Quem **não** tem permissão de escrever nesse caminho.
3. **Auditor em contexto limpo** — recebe só diff + log do falsificador; não vê a cadeia de pensamento do produtor.

Responda, em quatro linhas:

- Quando um módulo entra na fila? (dependências compilam **antes**.)
- Como o agente trapaceia se puder **stubar** um import que ainda não existe.
- Como trapaceia se puder **alterar o assert** (“aceitar qualquer status”).
- Como trapaceia se o proxy (yardstick) **não** for checado com Kendall contra a suíte lenta.

Não rode Antigravity. Não precisa de Gemini. O entregável é o desenho. Se o falsificador for um LLM-juiz, você falhou o exercício: juiz-LLM não é objetivo no sentido desta caixa.

---

## 6. O que fazer (e o que não fazer)

1. Ler o [blog](https://research.google/blog/advancing-science-engineering-with-antigravitys-teamwork-feature/) (13/11/2026) e o [post](https://x.com/mirrokni/status/2121351383236436247) com a secção 0 aberta.
2. Completar o exercício da secção 5.
3. Se estiver no A12, **não** cole 4,09× nem 800k linhas no ADR. Esses números não saíram da sua bancada.

Math/Lean/química/Deep Review aparecem no mesmo post. Ficam de fora desta caixa de engenharia de software de propósito: não misture prova formal de 50 M linhas com o collator do Amplitude.
