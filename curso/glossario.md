# Glossário

Termos como este repositório os **usa**. Não é um dicionário de IA: cada entrada aponta para onde o conceito aparece no material.

| Termo | Significado aqui | Onde ver |
| --- | --- | --- |
| **LLM** | Modelo de linguagem grande usado como componente de sistema (API, browser ou local), não como “oráculo”. | M01 §5–10; M02–M04 |
| **Token** | Unidade de texto cobrada/contada no contexto. Orçamento de contexto = limite de tokens por seção. | M01 tokenizer (README); M04 U5 `ContextBuilder` |
| **Temperature / top-K** | Aleatoriedade da amostragem. Temperature alta = mais variação; top-K limita o vocabulário candidato. | `exemplo-04-webai02-temperature-and-topK/` |
| **Prompt engineering** | Projeto de instruções, exemplos e formato de saída. Neste curso inclui JSON e TOON. | README raiz §6; M05/M07 system prompts |
| **TOON** | Formato compacto para dados em prompt (alternativa a JSON verboso para LLMs). | README raiz §6.2 |
| **System prompt / instructions** | Instrução persistente do modelo ou do agente de código (Copilot, AI Studio). | M04 U1 `.github/`; M07 `*-prompt.md` |
| **Web AI / Prompt API** | Inferência no Chrome (`LanguageModel`), às vezes Gemini Nano no dispositivo. | `exemplo-03` … `exemplo-05`; `troubleshooting/google.md` |
| **Embeddings** | Vetores que representam texto para similaridade. | `exemplo-12-*`; M04 U4 memória semântica; M09 datasets |
| **Vector store** | Índice de embeddings (aqui: Neo4j Vector Index, não “um Chroma genérico”). | `exemplo-12`, `exemplo-13`; M02 lab 06 |
| **RAG** | Retrieval-Augmented Generation: busca trechos e só então gera. Paper Lewis et al. | `exemplo-13`; M06 lab 10; M08 M4 |
| **Cypher** | Linguagem de consulta do Neo4j. No M02 o LLM **gera** Cypher. | `06-rag-neo4j-students-*` |
| **MCP** | Model Context Protocol: contrato de tools, resources e prompts entre host (IDE/agente) e servidor. | M01 §8; M03; M04 U3 `npm run mcp`; live 2026-02-24 |
| **MCP Inspector** | UI para depurar um servidor MCP (`mcp:inspect`). | M03 `05-mcps-do-zero-z` |
| **Tool / function calling** | Função que o modelo escolhe chamar (schema JSON). | M02 safeguard; M03; M04 U3; M08 tool canvas |
| **LangGraph / StateGraph** | Grafo de nós e arestas (incluindo condicionais) para fluxos com LLM. | M02; M03; M04 U6 |
| **ReAct** | Loop Pensamento → Ação → Observação. Paper Yao et al. | M04 U2; M06 lab 4; M08 M2 |
| **Plan-and-Execute** | Planeja passos e depois executa (contrasta com ReAct passo a passo). | M04 U2 |
| **Reflection** | Passo que critica/revisa a própria saída. | M04 U2/U4; M08 reflection canvas |
| **Spec-driven development (SDD)** | Spec → plano → tarefas → implementação (Spec Kit, `/especificar`). | M04 U1; live 2026-05-27 |
| **Guardrail** | Filtro ou política antes/depois do modelo (injection, dry-run, OPA). | M02 lab 05; M06 lab 11; M08/M09 |
| **Prompt injection** | Entrada que tenta sobrescrever instruções ou ler arquivos. | `05-safeguard-prompt-injection-*` |
| **HITL / Approval Gate** | Humano aprova ação de risco. HTTP 202 no OpsPilot; senha ChatOps; gate TrialForge. | M04 U7–U8; M06 labs 6 e 11; M08 M4 |
| **OpenRouter** | Gateway de vários modelos (incluindo `:free`) com uma API. | `exemplo-11`; M02–M04 |
| **Ollama** | Runtime local de modelos open-source. | `exemplo-10`; M08 padrão; M06 k8s complementar |
| **Groq** | Inferência rápida (Llama) usada pelo Nexus. | M06 `core/llm_config.py` |
| **AIOps** | IA aplicada a operações (métricas, incidente, remediação). | M06; M07 Risk Monitor (AIOps de **projeto**) |
| **IaC** | Infraestrutura como código (Terraform HCL nos labs Nexus). | M06 labs 1–2 |
| **GitOps / Canary** | Sync declarativo; rollout gradual com métricas. | M06 lab 3 |
| **FinOps** | Custo de nuvem como disciplina (zumbis, ROI). | M06 lab 9; lab 12 |
| **Trivy / CVE** | Scanner de vulnerabilidades; lab usa `data/trivy.json` (ex. XZ). | M06 lab 7 |
| **OPA / Checkov** | Políticas sobre HCL/K8s. | M06 `ui/` sandbox; `tools/` |
| **CrewAI** | Orquestração de agentes (Nexus: hierarchical no lab 12). | M06 |
| **Observabilidade** | Traces, logs, métricas. Grafana MCP no M01; `/stats` no OpsPilot; Jaeger **simulado** no M06. | M01 ex. 09; M04 U7; M06 labs 4–5; M08 M5 |
| **Context window / ContextBuilder** | Limite de contexto; montagem orçada por seção + sumarização em rolo. | M04 U5 |
| **Memória semântica** | Recall por embeddings, não só histórico linear. | M04 U4 |
| **Blackboard / supervisor** | Estado compartilhado e agente que despacha papéis. | M04 U9; M08 M3 |
| **Multiagente** | Mais de um papel/modelo coordenado (padrões Sequential, Parallel, Supervisor, Hierarchical, Group Chat, Handoff). | M04 U9; M08 M3 |
| **A2A** | Agent2Agent Protocol (referência de comunicação entre agentes). | README raiz M08 |
| **RICE / WSJF / MoSCoW** | Frameworks de priorização de backlog. | M07 M2 |
| **PERT / Monte Carlo** | Estimativa de três pontos; simulação de prazo (P50/P85/P95). **Script**, não LLM. | M07 M4 |
| **OKR** | Objetivos e resultados-chave; validados pelo OKR Aligner. | M07 M10 |
| **Danger** | Regras de PR como código. | M07 M8 |
| **OpenSpec** | Contratos/BDD para agentes no monorepo CFP. | M05 M3–M4 |
| **Genkit** | Orquestração de LLM no backend do BragBot. | M05 `modulo-05/brag-bot/` |
| **Stitch** | Geração de UI conversacional (Google), handoff para Angular. | M05 M2 |
| **LoRA / PEFT / QLoRA / DoRA** | Fine-tuning de poucos parâmetros (adaptadores). Pesos grandes fora do Git. | M09 M1 cheatsheet; M09 M4 |
| **Full fine-tuning** | Atualiza todos os pesos (caro; demo Colab/MLX no M09). | M09 M4 |
| **JSONL** | Um JSON por linha — formato de dataset de treino. | M09 M2–M6 |
| **MinHash + LSH** | Deduplicação aproximada de texto no dataset. | M09 M2 |
| **OCR vs multimodal** | Extrair campos de imagem via Tesseract/pipeline vs LLM que vê a imagem. | M09 M2 |
| **PII / Presidio** | Dados pessoais; gate de higienização. | M09 M2 |
| **AHP / NPV** | Decisão ponderada (Saaty) e valor presente líquido — “vale fine-tune?”. | M09 M1; reaparece no harness |
| **LLM-as-judge** | Modelo avalia saída de outro modelo. | M09 M5 companion |
| **Model tiering** | Cascata de modelos (barato → caro / local → fronteira). | M08 M5 |
| **Eval gate** | Promoção de modelo só após harness. | M08 M5; M09 M5 |
| **Vertex AI** | Fine-tuning gerenciado Google usado no M09. | M09 M3+ |
| **MLX** | Stack Apple Silicon para treino/inferência local. | M09 M4 |
| **Gabarito `-z`** | Solução da aula. | M01–M03 |
| **Snapshot** | Cópia completa do OpsPilot no fim da unidade N. | M04 |
| **Windowsfy** | Skill que sugere patches Unix→Windows nos `package.json`. | `skills/windowsfy/` |

Se um termo aparecer só em slide/vídeo e não nesta tabela, trate-o como opcional até existir pasta no repo.
