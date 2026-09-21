# Mídia do curso

Índice das capas e dos vídeos introdutórios da trilha **Engenharia de Software com IA Aplicada**.

As imagens ficam em [`imagens/`](./imagens/). As intros de módulo **versionadas neste repositório** são MP4 gerados com **Grok Imagine (xAI)** a partir dessas capas; estão em [`videos/grok/`](./videos/grok/). Os IDs HeyGen em [`videos/heygen-ids.json`](./videos/heygen-ids.json) continuam como referência complementar (os arquivos HeyGen **não** entram no Git). Use os MP4 Grok para playback local e no preview.

Estilo visual das peças HeyGen: **Blueprint** (`style_id`: `4c9025a3b9734c6ea6c122fc00e04767`).

## Imagens

Pré-visualização com caminho relativo a esta pasta. Capas 16:9 (1280×720).

| Preview | Arquivo | Descrição |
| --- | --- | --- |
| ![Capa do curso](imagens/curso-capa-hero.png) | [`imagens/curso-capa-hero.png`](imagens/curso-capa-hero.png) | Capa hero do curso: camadas de aplicação, serviços, domínio, dados e infraestrutura. |
| ![Capa do Módulo 01](imagens/modulo-01-capa.png) | [`imagens/modulo-01-capa.png`](imagens/modulo-01-capa.png) | Capa do Módulo 01 — Fundamentos de IA e LLMs (tokens, transformer e atenção). |
| ![Capa do Módulo 02](imagens/modulo-02-capa.png) | [`imagens/modulo-02-capa.png`](imagens/modulo-02-capa.png) | Capa do Módulo 02 — Integração de APIs de LLMs (gateway roteando vários modelos). |
| ![Capa do Módulo 03](imagens/modulo-03-capa.png) | [`imagens/modulo-03-capa.png`](imagens/modulo-03-capa.png) | Capa do Módulo 03 — MCP na prática (agente conectado a ferramentas e bases). |
| ![Capa do Módulo 04](imagens/modulo-04-capa.png) | [`imagens/modulo-04-capa.png`](imagens/modulo-04-capa.png) | Capa do Módulo 04 — Agentes autônomos (ciclo percebe → age → aprende; OpsPilot). |
| ![Capa do Módulo 05](imagens/modulo-05-capa.png) | [`imagens/modulo-05-capa.png`](imagens/modulo-05-capa.png) | Capa do Módulo 05 — IA para UI/UX (wireframe → dashboard → app). |
| ![Capa do Módulo 06](imagens/modulo-06-capa.png) | [`imagens/modulo-06-capa.png`](imagens/modulo-06-capa.png) | Capa do Módulo 06 — AIOps e engenharia agêntica (Nexus: pods, Prometheus, incidente). |
| ![Capa do Módulo 07](imagens/modulo-07-capa.png) | [`imagens/modulo-07-capa.png`](imagens/modulo-07-capa.png) | Capa do Módulo 07 — Gestão de projetos com IA (RouteWise: Kanban, OKR, backlog). |
| ![Capa do Módulo 08](imagens/modulo-08-capa.png) | [`imagens/modulo-08-capa.png`](imagens/modulo-08-capa.png) | Capa do Módulo 08 — Arquitetura de sistemas com IA (TrialForge: gateway → Approval Gate). |
| ![Capa do Módulo 09](imagens/modulo-09-capa.png) | [`imagens/modulo-09-capa.png`](imagens/modulo-09-capa.png) | Capa do Módulo 09 — Dados e fine-tuning (pipeline JSONL + adapters LoRA). |

## Vídeos Grok Imagine (intros por módulo)

Mídia **canônica versionada no Git**: image-to-video (~8 s) a partir das capas em `imagens/modulo-0N-capa.png`, gerada com **Grok Imagine (xAI)**. Metadados (`modulo`, `request_id`, `duration`, `status`) em [`videos/grok/manifest.json`](./videos/grok/manifest.json).

No preview local, os arquivos são servidos em `/media/videos/grok/modulo-0N-intro.mp4`.

Estas intros **substituem / complementam** os IDs HeyGen da seção seguinte: use o MP4 Grok para assistir e distribuir o pacote; os IDs HeyGen ficam como trilha alternativa na conta que gerou as peças.

| Módulo | Arquivo |
| --- | --- |
| 01 — Fundamentos de IA e LLMs | [`videos/grok/modulo-01-intro.mp4`](videos/grok/modulo-01-intro.mp4) |
| 02 — Integração de APIs de LLMs | [`videos/grok/modulo-02-intro.mp4`](videos/grok/modulo-02-intro.mp4) |
| 03 — MCP na prática | [`videos/grok/modulo-03-intro.mp4`](videos/grok/modulo-03-intro.mp4) |
| 04 — Agentes autônomos | [`videos/grok/modulo-04-intro.mp4`](videos/grok/modulo-04-intro.mp4) |
| 05 — IA para UI/UX | [`videos/grok/modulo-05-intro.mp4`](videos/grok/modulo-05-intro.mp4) |
| 06 — AIOps e engenharia agêntica | [`videos/grok/modulo-06-intro.mp4`](videos/grok/modulo-06-intro.mp4) |
| 07 — Gestão de projetos com IA | [`videos/grok/modulo-07-intro.mp4`](videos/grok/modulo-07-intro.mp4) |
| 08 — Arquitetura de sistemas com IA | [`videos/grok/modulo-08-intro.mp4`](videos/grok/modulo-08-intro.mp4) |
| 09 — Dados e fine-tuning | [`videos/grok/modulo-09-intro.mp4`](videos/grok/modulo-09-intro.mp4) |

## Vídeos HeyGen

Referência complementar (não é a mídia versionada no repo). Fonte dos IDs: [`videos/heygen-ids.json`](./videos/heygen-ids.json). Para obter o vídeo, use a API HeyGen com o `video_id` (por exemplo `GET /v1/video_status.get?video_id=…` na conta que gerou as peças). O arquivo de mídia HeyGen em si **não** está neste repositório — para playback no Git, use as intros Grok acima. Não invente URL de playback assinada.

| Título | Propósito | `video_id` |
| --- | --- | --- |
| Abertura do curso | Apresenta a pós, a trilha prática e o recorte de engenharia de software com IA aplicada. | `b6512fb935834e4c996eadc9d8ed5e2e` |
| Módulo 01 — Fundamentos de IA e LLMs | Abre o módulo de redes no cliente, Prompt API, prompts e RAG. | `0d316da2695c43d48e334c1e39fc5887` |
| Módulo 02 — Integração de APIs de LLMs | Abre o módulo de gateway, LangGraph, memória e guardrails. | `11e8981220ea49c2819a17c0d04351b8` |
| Módulo 03 — MCP na prática | Abre o módulo de tools, servidor MCP e API legado como MCP. | `22c37dad82184e7a8ce142a3607e2621` |
| Módulo 04 — Agentes autônomos | Abre o módulo OpsPilot (ReAct, memória, HITL, war room). | `fe1eeb502c854f51b13c5a430af0718a` |
| Módulo 05 — IA para UI/UX | Abre o módulo de discovery, Stitch/Figma → Angular, OpenSpec e Genkit. | `b071b9cc7f0740749d89c257eb91d2d3` |
| Módulo 06 — AIOps e engenharia agêntica | Abre o módulo Nexus (IaC, incidente, ChatOps, FinOps). | `b7abc6b8487a424785bba09e70e70160` |
| Módulo 07 — Gestão de projetos com IA | Abre o módulo RouteWise (RICE/WSJF, PERT, compliance). | `9531918b3f9c4350803fc9a126ce7662` |
| Módulo 08 — Arquitetura de sistemas com IA | Abre o módulo TrialForge (agente vs regra, RAG, Approval Gate). | `a542448445ff42e39de73c977e2dbd25` |
| Módulo 09 — Dados e fine-tuning | Abre o módulo Amplitude Seguros (AHP/NPV, JSONL, LoRA, harness). | `0dd3219c682749df984082c55a90d0c7` |

## Como regenerar

1. **Imagens** — gerar de novo com **Grok** (mesmo recorte 16:9, paleta escura e tema de cada módulo). Substituir o PNG em `imagens/` e conferir o preview nesta página.
2. **Intros Grok Imagine** — image-to-video (~8 s) a partir de `imagens/modulo-0N-capa.png`. Substituir o MP4 em `videos/grok/`, atualizar `request_id` / `duration` / `status` em `videos/grok/manifest.json` e a tabela acima. Não versionar `XAI_API_KEY` nem URLs temporárias de playback da xAI.
3. **Vídeos HeyGen** (complementar) — gerar de novo no **HeyGen Video Agent**, estilo **Blueprint** (`style_id` `4c9025a3b9734c6ea6c122fc00e04767`). Atualizar o `video_id` correspondente em `videos/heygen-ids.json` e na tabela HeyGen. Não versionar o MP4 HeyGen nem URLs temporárias de playback.
