<!-- titulo: Módulo 02 — Integração de APIs de LLMs -->

Olá. Seja bem-vinda, seja bem-vindo ao módulo dois.

No módulo um, o modelo de linguagem grande, o LLM, era uma chamada. Você comparou o runtime local com o gateway pela rede. Indexou um documento. Viu trechos voltarem. Agora o modelo precisa viver atrás de um contrato seu. HTTP. Grafo. Banco. Autorização.

A pergunta desta semana não é qual o melhor modelo. É outra. Quem escolhe o modelo. Quem guarda o estado. Quem impede o usuário de ler um arquivo. E quem corrige uma consulta inválida antes de bater no banco de grafos.

Ao final, você consegue expor um gateway que escolhe provedor e modelo. Desenhar um grafo com nós e arestas condicionais. Completar o fluxo de agendamento médico no template. Persistir preferência de usuário. Mostrar um bloqueio de injeção de prompt. E gerar Cypher, a linguagem de consulta do grafo, contra um conjunto de alunos e cursos.

Sete laboratórios. Nem todos chamam o modelo. Isso é de propósito.

O primeiro laboratório é um gateway Fastify. O cliente manda uma mensagem de chat. Ele não fala com a OpenRouter. Quem conhece a lista de modelos é o seu serviço. Quem escolhe o nome é a sua configuração. Force um nome inválido. Veja o erro, ou o caminho alternativo. Isso não é detalhe. É o mesmo padrão que o OpsPilot e o TrialForge vão chamar de gateway. Tem teste de ponta a ponta. Rode.

O segundo laboratório é LangGraph sem GPT. Sério. O grafo classifica maiúscula e minúscula por palavra-chave. Não pede token. O vocabulário que você precisa cabe aqui. Estado. Nó. Aresta. Aresta condicional. Sirva o estúdio. Se você sair daqui achando que LangGraph é sinônimo de modelo, volte e rode de novo. O vocabulário barato salva o laboratório caro.

O terceiro laboratório é o primeiro grafo de negócio. Consultas médicas. No template, o nó que identifica a intenção quase devolve o estado intacto. Tem log. Não tem chamada ao modelo. Você liga o prompt. Preenche a intenção. E o TypeScript decide se agenda, cancela, ou responde.

Saída estruturada. O modelo não conversa sobre medicina. Ele classifica para o serviço. Abra o desenho do grafo antes de escrever o nó. O desenho já existe. Falta o miolo.

Um cuidado. Vários textos internos falam de um gerador de artigos. Ignore. A especificação é o guia do curso, o plano do laboratório de Cypher, e o código-fonte.

O quarto laboratório tem duas pessoas. Erick e Ana. Postgres sobe com o compose. A conversa é de curto prazo. A preferência, o gosto musical, o destaque, é de longo prazo, e mora no banco. Se o processo Node cair e o gosto sumir, você não persistiu. Mais à frente, no OpsPilot, a memória vai ser semântica. Aqui ela é tabela. Os dois existem em produção.

O quinto laboratório é injeção de prompt. Há um membro seguro e um membro inseguro. Os dados estão numa lista de usuários. O membro tenta ler um arquivo. Tem que falhar. Um papel privilegiado pode passar. Demonstre os dois. Nunca autorize com o texto do atacante. O guardrail é código. Não é um parágrafo no prompt de sistema.

O sexto laboratório muda o contrato do RAG. No módulo um, o modelo lia trechos de um PDF. Aqui ele escreve Cypher contra alunos e cursos. Siga o plano do laboratório, não o texto interno. Infraestrutura. Semente. Teste de ponta a ponta. Pergunte o ranking de um curso. Cole a consulta gerada. O loop de correção existe porque o grafo não entende português. Ele entende Cypher.

Há um sétimo laboratório, de análise de documento. É opcional se o Cypher já fechou o ponto de verificação. Use um arquivo seu. Não procure um PDF pronto no clone. Ele não está lá.

Trabalhe no template. Entregar o gabarito não conta. Uma interface LangGraph. Um texto curto de como subir. Testes verdes. E um parágrafo do que o gabarito fez diferente.

No módulo três, esse contrato vira protocolo de contexto de modelo, o MCP. Ferramentas de verdade. Token de serviço. O agente para de improvisar acesso a banco.

Até lá, escolha um eixo. Gateway com o fluxo médico. Ou salvaguarda com a consulta Cypher. Suba. Quebre o nome do modelo de propósito. Mostre o bloqueio. Mostre a consulta. Esse é o módulo em que o LLM deixa de ser uma chamada, e vira peça de sistema.
