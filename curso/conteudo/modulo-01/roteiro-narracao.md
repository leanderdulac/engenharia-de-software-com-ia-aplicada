<!-- titulo: Módulo 01 — Fundamentos de IA e LLMs para programadores -->

Olá. Seja bem-vinda, seja bem-vindo ao módulo um da pós Engenharia de Software com IA Aplicada.

Respire. Esta aula é calma de propósito.

Você já escreve software. Ninguém pede que você vire cientista de dados nesta semana. O pedido é outro. Trate o modelo como um componente. Um binário no Node. Um trabalhador em segundo plano no navegador. Uma interface de prompt no Chrome. Um processo na sua máquina. Ou uma chamada pela rede.

O mercado quer que você pule direto para o chat. Esta trilha faz o caminho inverso. Primeiro uma rede pequena. Depois um recomendador no navegador. Depois um detector atira no pato. Só então o texto entra. No fim, você busca trechos, e só depois gera a resposta.

Ao sair daqui, você aponta cinco lugares. Um modelo seu, no Node. Um modelo de visão no cliente. Um modelo de linguagem no dispositivo. Um modelo local versus um modelo pela rede. E um modelo com documentos, usando geração aumentada por recuperação, o RAG.

Vamos com calma.

No primeiro exemplo do módulo, o comentário ainda fala de pessoas. Erick. Ana. Carlos. Idade, cor, cidade. A rede não vê isso. Ela vê um vetor. Números. Idade normalizada. Cor em código one-hot. Cidade em código one-hot. Isso não é detalhe pedagógico. É o contrato. Modelos de linguagem grandes, os LLMs, redes de visão e embeddings fazem a mesma conversão. Texto ou pixel vira tensor. Só que com milhões de parâmetros a mais.

Seu trabalho, nesse primeiro exemplo, é completar o treino e fazer uma predição. O gabarito existe, na pasta de laboratório. Abra depois. Não na primeira subida.

A loja de recomendações coloca a mesma ideia no navegador. O treino mora num trabalhador em segundo plano. A vitrine quase não muda. O que evolui é o modelo.

Depois vem o jogo. Aqui não há prompt. Há um detector You Only Look Once, o YOLO, no cliente. Você carrega o modelo. Depois ajusta o limiar. Jogue. Erre um pato. Acerto e erro são métrica visível. Visão no navegador tem latência de quadro. Não é agente. Não precisa ser. Guarde isso para o dia em que alguém quiser um agente para um problema que é só um classificador.

Só então entra o texto.

O modelo de linguagem não sabe. Ele amostra o próximo token. Dois controles que este curso obriga você a sentir. Temperatura. Quão plana é a distribuição. Zero é guloso. Um é criativo e instável. E o top-K. Quantos tokens candidatos entram no sorteio.

Faça a mesma pergunta no zero e no um. Anote o que mudou. Amostragem não é oráculo.

Há também um exemplo com streaming no Chrome, e outro que soma imagem e áudio. Se a interface de prompt falhar, não trave a semana. Tem Ollama, o runtime local. Tem OpenRouter, o gateway pela rede. O ponto de verificação aceita um caminho alternativo documentado.

Prompt com saída estruturada também entra aqui. JSON, o formato de objetos. Ou TOON, o formato compacto. Quando um programa consome a resposta, peça estrutura. Texto livre é para humano.

O protocolo de contexto de modelo, o MCP, neste módulo é consumo, não autoria. Você cola um prompt. Gera testes. Preenche um formulário. Investiga um vazamento no Grafana. Ou roda a demonstração já pronta. Escolha um. Quatro no mesmo dia não é virtude.

Ollama e OpenRouter recebem o mesmo tipo de chamada. Um fica na sua máquina. O outro sai pela rede. Anote latência, qualidade, e se o dado saiu do computador. Dez linhas de comparação bastam. Essa tabela volta mais à frente, como decisão de arquitetura.

O fechamento é a geração aumentada por recuperação. Um PDF vira embedding no Neo4j, o banco de grafos. Você sobe a infraestrutura. Indexa o documento. Busca trechos. Só então gera. Sem trecho visível, não é RAG. É um modelo educado. A pasta de respostas do gabarito existe. Leia depois da sua pergunta.

Trabalhe no template. Não copie o gabarito. No Windows, a ligação nativa do TensorFlow costuma doer. O Linux no Windows ajuda.

Ao sair daqui, você distingue modelo no cliente, modelo local, e modelo via interface. E você já viu recuperação de verdade.

No próximo módulo, esse modelo de linguagem entra atrás de um gateway. E o grafo deixa de ser metáfora.

Até lá, complete o laboratório de embeddings. Faça uma pergunta. Mostre os trechos. Esse é o seu primeiro sistema com inteligência artificial aplicada.
