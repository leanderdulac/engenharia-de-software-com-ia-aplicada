# Ementa — Engenharia de Software com IA Aplicada

Pós-graduação. Material prático neste repositório; aulas em vídeo fora do Git. Este documento descreve **o que o curso ensina**, não um tratado genérico de engenharia de software.

## Identificação

| Campo | Conteúdo |
| --- | --- |
| Nome | Engenharia de Software com IA Aplicada |
| Natureza | Pós-graduação lato sensu (disciplina / trilha completa) |
| Carga horária | 240 h de estudo dirigido (ver [trilha-aprendizado.md](./trilha-aprendizado.md)) |
| Linguagens | TypeScript/Node (eixo), Python (paridade nos M06–M09 e labs Nexus) |
| Licença do material | [CC BY-NC-ND 4.0](../LICENSE.md) |

## Objetivos gerais

Ao final, o aluno projeta, implementa, avalia e governa software que **usa modelos de linguagem e agentes como componentes de sistema** — com o mesmo rigor de API, teste, observabilidade e decisão de arquitetura que se espera de software de produção.

## Objetivos específicos

1. Distinguir ML clássico no cliente (TF.js, visão) de LLMs e de agentes com tools.
2. Integrar provedores (OpenRouter, Ollama, Groq, Vertex, Gemini) atrás de contratos estáveis.
3. Implementar RAG, memória semântica e orçamentos de contexto com evidência mensurável.
4. Publicar e consumir MCP com autenticação, rate limit e registry.
5. Construir um agente evolutivo (OpsPilot) até war room + modo equipe.
6. Usar IA no ciclo de produto (discovery, UI, E2E, backend Genkit).
7. Operar AIOps com HITL (Nexus) e gestão assistida (RouteWise) sem abdicar de critério.
8. Arquitetar sistemas agentic com Approval Gate e trilha de auditoria (TrialForge).
9. Decidir fine-tuning com AHP/NPV e executar LoRA ou API gerenciada com harness (Amplitude Seguros).

## Conteúdo programático

Unidades alinhadas às pastas reais. Detalhe operacional em [`modulos/`](./modulos/).

### Unidade 1 — Fundamentos de IA e LLMs para programadores (M01)

Redes no Node e no browser; recomendação; visão (YOLO + Duck Hunt); Web AI (Prompt API, temperature/top-K, multimodal); prompt engineering e TOON; agentes de código; MCP (Playwright, Context7, Grafana); Ollama vs proprietário; OpenRouter; embeddings e RAG com Neo4j.

### Unidade 2 — Integração de APIs de LLMs (M02)

Gateway de roteamento de modelos; intro LangGraph; cadeia de agendamento médico; recomendador com memória e Postgres; guardrails de prompt injection; Text-to-Cypher sobre grafo de cursos; Q&A de documentos.

### Unidade 3 — MCP na prática (M03)

Agente com múltiplas tools MCP; tool SerpAPI/Google Trends; instructions de agente no IDE; Agent Skills; MCP do zero (crypto); API legado como MCP; JWT/RBAC/service token; publicação em npm privado (Verdaccio); LangChain + MultiServer MCP.

### Unidade 4 — Criação de agentes autônomos (M04)

Notas API com Copilot e Spec-Driven Development; OpsPilot: ReAct / Plan-and-Execute / Reflection; function calling, SQLite, MCP; memória e refletor; ContextBuilder; LangGraph de produção; observabilidade e HITL; war room publicado; multiagente (supervisor + blackboard).

### Unidade 5 — IA para UI/UX (M05)

Refinamento e data discovery (Pix agendado); Stitch/Figma → Angular (Pix App); OpenSpec + agentes no monorepo CFP; E2E/MCP; BragBot com Genkit.

### Unidade 6 — AIOps e engenharia agêntica (M06)

Doze labs Nexus: fundação, IaC Copilot, K8s/GitOps, ReAct troubleshooting, AIOps preditivo, ChatOps, DevSecOps/Trivy, CI/CD, FinOps, RAG de runbook, guardrails, orquestração hierárquica.

### Unidade 7 — Gestão de projetos com IA (M07)

Dez ferramentas sobre RouteWise: Requirements Copilot, RICE/WSJF, scheduling, PERT+Monte Carlo, Risk Monitor, Meeting Digest, Status Report, compliance+Danger, NL→Jira, OKR Aligner.

### Unidade 8 — Arquitetura de sistemas com IA (M08)

TrialForge: diagrama AI-first; single-agent ReAct; seis padrões multiagente; RAG avançado + gateway HITL; enterprise (tiering, eval gate, observabilidade).

### Unidade 9 — Processamento de dados e fine-tuning (M09)

Amplitude Seguros: decision framework (AHP/NPV); dataset JSONL, PII, OCR vs multimodal; Vertex AI; LoRA/PEFT (MLX ou Colab); harness de avaliação; capstone 3.000 exemplos.

### Atividades complementares

Lives em [`lives/`](../lives/) (MCP/skills, SDD, Safer). Não entram na nota salvo o instrutor decidir (ver [avaliacao.md](./avaliacao.md)).

## Metodologia

- **Aprender no código do repo.** Cada aula aponta para pasta `*-template` ou snapshot `UNIDADE.md` / lab `.py` / `*-prompt.md` / canvas.
- **Gabarito depois da tentativa.** Pastas `*-z` e outputs de exemplo existem para comparação, não para copiar no primeiro passo.
- **Paridade JS/Python** nos Módulos 07–09 e protótipos do 08–09: escolha uma linguagem e seja consistente; a outra é referência.
- **Casos âncora** (OpsPilot, Nexus, RouteWise, TrialForge, Amplitude) carregam o módulo inteiro — não misture casos no mesmo entregável.

## Bibliografia

Só o que já está citado no material do repo. Completar com os links do [README da raiz](../README.md).

### Obrigatória (papers e padrões usados nas aulas)

- Lewis et al. — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (NeurIPS 2020). Ligado ao M01 §10 e M08 M4. Link no README: `https://arxiv.org/abs/2005.11401`.
- Yao et al. — *ReAct: Synergizing Reasoning and Acting in Language Models* (ICLR 2023). M04 U2, M06 lab 4, M08 M2. `https://arxiv.org/abs/2210.03629`.
- Hu et al. — *LoRA: Low-Rank Adaptation of Large Language Models* (2021). M09 M4. `https://arxiv.org/abs/2106.09685`.
- Dettmers et al. — *QLoRA: Efficient Finetuning of Quantized LLMs* (NeurIPS 2023). M09 M1/M4. `https://arxiv.org/abs/2305.14314`.
- Lee et al. — *Deduplicating Training Data Makes Language Models Better*. M09 M2. `https://arxiv.org/abs/2107.06499`.
- [Model Context Protocol](https://modelcontextprotocol.io/) — Anthropic. M01 §8, M03, M04 U3, M08 M2.
- Documentação OpenRouter, Ollama, Playwright MCP, Context7, CrewAI, LangGraph — conforme cada módulo.

### Complementar (já linkada no README ou nos módulos)

- Prompt engineering: OpenAI, Anthropic *Effective context engineering for AI agents*, Claude 4 best practices.
- Gestão: RICE (Intercom), WSJF (SAFe), MoSCoW, PERT, Planning Fallacy (Kahneman & Tversky).
- Arquitetura: CAP theorem; [A2A Protocol](https://a2a-protocol.org/); RAND *Why AI Projects Fail* (M08).
- Fine-tuning: companions na raiz do M09 (`casos-de-mercado-fine-tuning-companion.md`, `historico-fine-tuning-companion.md`, *Bestiário do Zoo*).
- IBM Cost of a Data Breach Report 2025 (M07 M8).
- Saaty — Analytic Hierarchy Process (M09 M1).

Não acrescente URLs “canônicas” que não estejam no README ou nos módulos: o pacote recusa links inventados.

## Critérios de avaliação (resumo)

Detalhe e rubricas em [avaliacao.md](./avaliacao.md).

| Componente | Peso sugerido |
| --- | --- |
| Checkpoints de lab (M01–M03, M06) | 30% |
| Projetos âncora de módulo (OpsPilot, Nexus 12, RouteWise, TrialForge, Amplitude) | 50% |
| Participação em demos / curadoria (prompts, canvases, HITL) | 10% |
| Integração final (opcional: cruzar dois casos) | 10% |

Aprovação: média ≥ 7,0 **e** checklist de conclusão de pelo menos 7 dos 9 módulos (os 7 devem incluir M04 e um entre M06/M08/M09). O instrutor pode adaptar pesos à calendário da turma; não avalie o que o lab não pede.

## Recursos e restrições

- Sem vídeos neste Git. Sem PRs externos ([LICENSE.md](../LICENSE.md)).
- M09 tem custo real de Vertex AI (ordem de grandeza documentada no README do módulo). Há rota Colab/MLX sem nuvem paga.
- Pasta `modulo04-agentes-autonomos/` (versão antiga citada no README da raiz) **não está neste clone**. Use só [`modulo04-criacao-de-agentes-autonomos-novo/`](../modulo04-criacao-de-agentes-autonomos-novo/).
