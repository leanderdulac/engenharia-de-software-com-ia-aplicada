![Capa do Módulo 06 — AIOps e engenharia agêntica](../../media/imagens/modulo-06-capa.png)

# Módulo 06 — AIOps e engenharia agêntica (Nexus)

Guia: [`curso/modulos/06.md`](../../modulos/06.md). Pasta: [`modulo06-aiops-engenharia-agentica/`](../../../modulo06-aiops-engenharia-agentica/). README operacional: [`README.md`](../../../modulo06-aiops-engenharia-agentica/README.md). Carga: ~28 h, **12 labs**. Teoria extra em [`slides/`](../../../modulo06-aiops-engenharia-agentica/slides/).

O Nexus é o caso âncora de operação: agentes CrewAI + Groq (Llama) geram IaC, diagnosticam pod, falam no “Slack”, triam CVE, caçam zumbi de nuvem e fecham um incidente **multidomínio** com relatório executivo. Prometheus e Jaeger, neste material, são **simulados** no lab 4. Ollama no cluster (`k8s/ollama.yaml`) é complementar, não pré-requisito.

---

## Abertura

Você já viu ReAct no OpsPilot (ou no paper). Agora o loop pensa-age-observa em **infraestrutura**. A fantasia é o agente aplicar `kubectl delete` sozinho às três da manhã. A aula é o contrário: gerar HCL com auditoria, dry-run, senha de gestor, OPA, e um Manager hierárquico que **escreve relatório** — não um botão vermelho sem dono.

Python **3.10–3.13**, não 3.14 (CrewAI/Pydantic). `GROQ_API_KEY` exportada — o README não cria `.env`. Menu: `python3 nexus_iac_copilot.py`. Dashboard opcional: `streamlit run ui/app.py` (LocalStack :4566 se for explorar S3). Código dos agentes em [`core/agents.py`](../../../modulo06-aiops-engenharia-agentica/core/agents.py), tools em [`tools/`](../../../modulo06-aiops-engenharia-agentica/tools/), manifests em [`k8s/`](../../../modulo06-aiops-engenharia-agentica/k8s/).

Ao final: labs 1–2 com `main.tf` auditável; um diagnóstico (lab 4) **ou** ChatOps (lab 6); um de {7, 9, 10}; e os labs 11 **e** 12 com o parágrafo do que você não deixaria o Manager aplicar sozinho.

---

## Conceitos (12 labs, uma esteira)

### Fundação e IaC com auditoria (labs 1–2)

[`labs/modulo1_foundation.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo1_foundation.py) — S3 de logs + `check_compliance_rules`. Não é “o modelo inventa um bucket”. É desenho com regra: criptografia, bloqueio de público, tag de dono — o que a função de compliance do lab realmente checa. Leia `core/` e `tools/` quando o HCL “passar” e você não souber **qual** regra passou. O menu `nexus_iac_copilot.py` só dispara; a inteligência (e o auditor) estão nesses módulos.

[`labs/modulo2_iac_copilot.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo2_iac_copilot.py) — gera/audita `main.tf`. O arquivo `main.tf` também existe na raiz do módulo como artefato de trabalho. A lição: o copiloto de Terraform **não** substitui o auditor. No código, o papel de DevSecOps Auditor existe de propósito. Você compara o HCL com política. No UI, o sandbox OPA faz o gesto visual. Se o lab reescrever um `aws_s3_bucket` sem `block_public_acls` e o auditor não reclamar, o exercício de conformidade falhou — mesmo que o Llama tenha escrito HCL “bonito”.

### Kubernetes declarativo e Canary (lab 3)

[`labs/modulo3_k8s_ops.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo3_k8s_ops.py) — manifesto + decisão de Canary. GitOps aqui é a ideia de reconciliação: o cluster **tende** ao declarado. Canary é métrica, não coragem. Sem baseline, “vamos de 100%” é chute.

### ReAct de incidente (lab 4)

[`labs/modulo4_troubleshooting.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo4_troubleshooting.py). **Antes:** `kubectl apply -f k8s/deploy.yml` (pod quebrado de propósito). Depois o SRE de plantão. CrashLoop / imagem errada. Thought → kubectl/métrica simulada → observação → hotfix. É o irmão do OpsPilot U2, com `kubectl` no lugar de `list_alerts`. Cluster local só é obrigatório neste lab e no 11, se você for aplicar manifesto de verdade.

Não cole o hotfix no cluster sem ler. O lab gera a correção; o aprendizado é o **rastro ReAct**. Se a causa raiz no seu caderno for “o modelo disse que é OOM” e o `deploy.yml` na verdade aponta imagem inexistente, você avaliou o prosa e não o YAML. Abra o manifesto. Confira o campo `image`. Aí o loop fecha.

### Preditivo e linguagem de métrica (lab 5)

[`labs/modulo5_aiops.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo5_aiops.py) — NL → PromQL, alerta preditivo (regressão de disco), JSON de dashboard Grafana. O modelo não “vê o futuro”. Ele ajusta uma reta sobre série e você decide se o alerta merece página. Relacione com o Grafana MCP do M01: lá você **consumia** a stack; aqui você **gera** o artefato.

### ChatOps e a senha que existe para ser usada (lab 6)

`streamlit run labs/modulo6_chatops.py`. Tente `@nexus-bot destrua o banco de dados`. O robô pede `GESTOR-APROVA`. Isso não é easter egg: é HITL didático. Sem a senha, ação destrutiva não passa. Compare com o 202 do OpsPilot: lá o protocolo é HTTP; aqui é teatro de Slack. O princípio é idêntico.

### Sec, CI, dinheiro, runbook (labs 7–10)

| Lab | Arquivo | Entrada no disco | O que você demonstra |
| --- | --- | --- | --- |
| 7 DevSecOps | [`labs/modulo7_devsecops.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo7_devsecops.py) | [`data/trivy.json`](../../../modulo06-aiops-engenharia-agentica/data/trivy.json) | Triagem CVE (o material cita XZ / CVE-2024-3094 no README da raiz e do módulo) |
| 8 CI/CD | [`labs/modulo8_cicd.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo8_cicd.py) | [`data/workflow_lento.yaml`](../../../modulo06-aiops-engenharia-agentica/data/workflow_lento.yaml) | Cache de dependência, workflow menos lento |
| 9 FinOps | [`labs/modulo9_finops.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo9_finops.py) | [`data/inventario_cloud.json`](../../../modulo06-aiops-engenharia-agentica/data/inventario_cloud.json) | Zumbis (IP/EBS), ROI do corte |
| 10 RAG | [`labs/modulo10_remediation.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo10_remediation.py) | [`data/runbook_db.md`](../../../modulo06-aiops-engenharia-agentica/data/runbook_db.md) | Remediação **citando** o runbook, não inventando comando |

O lab 10 é o RAG do M01 em farda de SRE. Sem trecho do `runbook_db.md`, o plano de “aumentar conexão do banco” é alucinação operacional — a pior.

### Guardrail e o game day (labs 11–12)

[`labs/modulo11_guardrails.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo11_guardrails.py) — dry-run + aprovação `sim`/`nao` no terminal. O agente **sugere** o `kubectl`; você autoriza. Sem dry-run, não há lab.

[`labs/modulo12_projeto_final.py`](../../../modulo06-aiops-engenharia-agentica/labs/modulo12_projeto_final.py) — checkout 500 + backdoor XZ + custo +40%. O **Nexus Manager** coordena SRE, Segurança e FinOps em hierarquia CrewAI e emite relatório executivo. C06.4 pede 11 **e** 12. O projeto do módulo é este relatório mais 15 linhas: o que você **não** deixaria o Manager aplicar sozinho em produção, amarrado ao lab 11.

Três sinais de que o relatório do 12 está só “bem escrito”: (1) não cita o CVE do `trivy.json` nem o zumbi do inventário; (2) sugere `kubectl apply` sem dry-run; (3) mistura o checkout 500 com um corte de custo como se fossem o mesmo change. O Manager hierárquico existe para **separar** papéis. Seu parágrafo de autonomia deve nomear pelo menos uma ação de cada domínio (SRE, Sec, FinOps) que ficaria atrás do `nao`.

---

## Passo a passo

```bash
cd modulo06-aiops-engenharia-agentica
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install streamlit
export GROQ_API_KEY=...
python3 nexus_iac_copilot.py
```

1. Labs 1–2 pelo menu ou `python3 labs/modulo2_iac_copilot.py`. Guarde o `main.tf` e o parecer da auditoria.
2. Lab 3 se quiser o YAML; não bloqueia o checkpoint C06.1.
3. Lab 4: aplique o deploy quebrado, rode o troubleshooting, anote a causa. **Ou** lab 6: o desafio da senha (C06.2 pede um dos dois).
4. Um de 7, 9 ou 10 com o JSON/Markdown de saída (C06.3).
5. Lab 11: recuse uma vez (`nao`) e aceite outra com dry-run ok.
6. Lab 12: cole o relatório. Escreva as 15 linhas de autonomia.

Slides `slides1.md`–`slides12.md` são opcionais. Úteis se o lab parecer “script mágico”.

---

## Armadilhas

- **Python 3.14.** O README avisa. CrewAI quebra. Use 3.10–3.13.
- **`ModuleNotFoundError: crewai`.** Venv não está ativo. Não é o lab.
- **Achar que Prometheus/Jaeger estão no Docker deste lab 4.** São simulados. O Grafana de verdade que você viu no M01 é outro exercício.
- **Pular o `kubectl apply` do lab 4** e “imaginar” o CrashLoop. O diagnóstico sem pod é teatro.
- **Digitar a senha do lab 6 no PDF da turma em texto claro como se fosse produção.** É string didática `GESTOR-APROVA`. O que importa é o **fluxo** de recusa.
- **Lab 10 sem abrir `runbook_db.md`.** RAG sem retrieval visível — você já tomou bronca no M01.
- **Lab 12 sem o 11.** Relatório bonito sem dry-run é exatamente o anti-objetivo.
- **Exportar `GROQ_API_KEY` só no Discord.** A variável é no shell do venv.

---

## Síntese

AIOps neste curso não é um produto de mercado. É uma esteira: conformidade → IaC → deploy → incidente → preditivo → chat com freio → CVE → CI → custo → runbook → dry-run → orquestração hierárquica. Cada lab acrescenta um **papel** (auditor, SRE, FinOps) e um **freio**.

O RouteWise (M07) vai falar de risco de **projeto** (fluxo do board). O Nexus fala de risco de **produção**. Não misture os relatórios. O HITL é o vocabulário comum.

Antes do game day, relia `core/llm_config.py` só para saber **qual** modelo Groq o lab espera. Trocar o nome no escuro quebra o CrewAI de um jeito que parece “lab 12 instável”. Não é. É config. O mesmo vale para `kubectl` fora de contexto: manifests em `k8s/` são didáticos; aplicar `nexus-api-error-k8s.yaml` no cluster da empresa não é o exercício. O lab 8 lê `data/workflow_lento.yaml` — um Actions lento de **exemplo**, não o CI deste repositório da pós (que testa a skill windowsfy). Separe o caso Nexus do Git da disciplina.

O dashboard `ui/app.py` impressiona. Não substitui o relatório do 12 nem o `nao` do 11. Beleza de Streamlit não é evidência de governança.

---

## Exercício de fixação

**Game day em miniatura** (mesmo se o lab 12 for depois):

1. Trecho do `main.tf` + uma regra de compliance que ele passa ou falha (labs 1–2).
2. Causa raiz do pod **ou** print do ChatOps pedindo senha.
3. Um artefato: parecer Trivy, lista de zumbis, **ou** plano com citação do runbook.
4. Relatório do lab 12 (quando rodar) + 15 linhas: três ações que exigiriam `nao` no lab 11 em produção real, e por quê.

Sem o item 4 o módulo não fecha. Sem os itens 1–3 você chega no 12 sem repertório.
