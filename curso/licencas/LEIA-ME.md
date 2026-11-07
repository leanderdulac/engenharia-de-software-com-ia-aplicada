# Licenças, adaptação e distribuição

Isto **não** é parecer jurídico. Atribuição **não** é autorização. Isolar o material Apache **não** libera o tronco CC BY-NC-ND.

## O que está no disco

| Árvore | Licença no arquivo | O que isso implica *neste* repo (leitura operacional, não aconselhamento) |
| --- | --- | --- |
| Tronco UniPDS (`curso/`, `modulo01`–`09`, `lives/`, `skills/`, …) | [CC BY-NC-ND 4.0](../../LICENSE.md) | Estudo privado; partilhar o **original** com crédito; **sem** uso comercial; **ND** = redistribuir material *adaptado* pode ser proibido |
| Ilha [`referencia/llm-course/`](../../referencia/llm-course/) | Apache-2.0 ([LICENSE](../../referencia/llm-course/LICENSE), [NOTICE](../../referencia/llm-course/NOTICE)) | Seguir o Apache **dessa pasta**. A UniPDS não relicencia isso como CC |
| Labs com `LICENSE` próprio (ex. Duck Hunt, templates Fastify) | O ficheiro ao lado do código | Não misturar com o tronco nem com o Apache da ilha |
| Mídia em [`curso/media/`](../media/README.md) | Tronco + termos dos geradores (Azure TTS, xAI Grok, HeyGen) | Não regenerada nesta estabilização; IDs HeyGen não incluem o MP4 |

Aviso do tronco também está no [NOTICE](../../NOTICE) da raiz.

## Estudo privado / fork versus distribuição

**Estudo privado e fork pessoal** (clonar, anotar, adaptar *para si*, entregar checkpoint no LMS da turma) é o uso descrito em [LICENSE.md](../../LICENSE.md) e no [guia do aluno](../guia-do-aluno.md).

**Distribuição** é outra coisa: publicar o pacote adaptado (site público, Pages, espelho, PDF comercial, curso pago, “meu GitHub com o material reescrito”). O termo **NoDerivatives** da CC BY-NC-ND 4.0 diz que quem transforma o material **não pode distribuir** o material modificado. Converter Markdown em HTML de preview, reorganizar guias e acrescentar rubricas *pode* ser visto como adaptação — **só um jurista dos titulares decide**.

Consequência operacional **deste** pacote:

- O preview **local** e os testes CI são para a turma acompanhada / o coordenador.
- Um build estático para GitHub Pages **existe e é verificável**. **Não** afirmamos URL pública persistente. **Não** ligámos Pages, DNS, nem conta.
- Publicação pública das adaptações deste PR deve esperar **autorização dos titulares** (Unipds Educação / autores originais informados) **ou** revisão jurídica. Até lá, trate Pages/espelhos públicos como **bloqueados**.
- Partilhar o **link do repositório original, sem modificar o conteúdo** continua a ser o caminho CC de “Share”.

## O que este trabalho não fez

- Não relicenciou trabalho alheio.
- Não apagou NC/ND.
- Não enviou e-mails, pedidos de permissão, pagamentos nem mensagens externas.
- Não tratou o vendor Apache como “já podemos comercializar o curso”.
- Não ouviu os MP3/MP4 para atestar qualidade pedagógica da narração.

## Documentos internos (não enviar)

- [modelos-pedido-permissao.md](./modelos-pedido-permissao.md) — rascunhos para o coordenador colar num canal oficial, **se** os titulares pedirem por escrito.
- [plano-conteudos-originais.md](./plano-conteudos-originais.md) — o que dá para substituir por texto original da pós se a autorização de adaptação/redistribuição não vier.

## C-COLAB e o preprint

O checkpoint opcional cita arXiv:2611.02633v1 (*Measuring AI Agents as Teammates with Collaborative Intelligence*). A citação é crédito de método, **não** licença para copiar o benchmark, as 240 tarefas, figuras ou ranking. Confirmado de novo em 7 nov. 2026 em <https://arxiv.org/abs/2611.02633>. Não é reprodução oficial do CIB.
