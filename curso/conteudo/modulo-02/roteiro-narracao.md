<!-- titulo: Módulo 02 — Integração de APIs de LLMs -->

No Módulo 01 o LLM era uma chamada. Agora ele precisa viver atrás de um contrato seu.

Primeiro lab. Um gateway Fastify. POST barra chat. O cliente não fala OpenRouter. Quem escolhe modelo é o seu serviço. Config e openrouterService. Force um nome inválido. Veja o erro ou o fallback. Isso não é detalhe. É o mesmo padrão que o OpsPilot e o TrialForge vão chamar de gateway. Tem teste E2E. Rode.

Segundo lab. LangGraph sem GPT. Sério. O grafo classifica maiúscula e minúscula por palavra-chave. Estado, nó, aresta, aresta condicional. Sirva o studio. Se você sair daqui achando que LangGraph é sinônimo de modelo, volte e rode de novo. O vocabulário barato salva o lab caro.

Terceiro lab. Consultas médicas. O template deixa o identifyIntent quase vazio. Tem try catch. Tem log. Não tem chamada ao modelo. Você liga o prompt da pasta v1, preenche a intenção, e o TypeScript decide se agenda, cancela ou responde. Structured output. O modelo não conversa sobre medicina. Ele classifica para o serviço. Abra o grafo e a factory antes de escrever o nó. O desenho já existe.

Cuidado vermelho. Vários READMEs falam de gerador de artigos. O package.json do médico às vezes ainda traz esse nome. Ignore. Spec é o guia do curso, o plan.md do lab seis, e a pasta src.

Quarto lab. Duas pessoas. Erick e Ana. Postgres no compose. Preferência não é o histórico do chat. Se o processo Node cair e o gosto musical sumir, você não persistiu. No OpsPilot a memória vai ser semântica. Aqui ela é tabela. Os dois existem em produção.

Quinto lab. Prompt injection. Scripts de membro seguro e membro unsafe. Dados em users.json. O membro tenta ler arquivo. Tem que falhar. Um papel privilegiado pode passar. Demonstre os dois. Nunca autorize com o texto do atacante. O template não tem pasta tests apesar do README. O z ainda traz mcpService. Não copie o MCP para fingir que o lab de safeguard acabou.

Sexto lab. O LLM escreve Cypher. Não é o RAG do PDF do módulo um. Lá o modelo lê trechos. Aqui ele escreve consulta contra alunos e cursos. Siga o plan.md. Infra, seed, E2E. Pergunte o ranking de um curso. Cole a consulta gerada. O loop de correção existe porque o grafo não entende português.

O lab sete sobe na porta 4000. Não há PDF no clone. Não há tests no disco. Use um arquivo seu. É opcional se o Cypher já fechou o checkpoint.

Trabalhe no template. Entregar o z não conta. Uma API LangGraph, um README de vinte linhas, testes verdes, um parágrafo do que o gabarito fez diferente.

No módulo três esse contrato vira MCP. Tools de verdade. Token de serviço. O agente para de improvisar acesso a banco.
