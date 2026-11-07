# Protocolo operacional — piloto acompanhado

Versão de trabalho para o coordenador. **Proposta**, não dados reais de turma. Ninguém foi recrutado nem contactado. Um dry-run técnico (preview, C-COLAB, labs offline) **não** valida aprendizagem.

Licença e publicação pública: [`../licencas/LEIA-ME.md`](../licencas/LEIA-ME.md). Enquanto não houver autorização dos titulares, o piloto corre em **clone privado / LMS**, sem Pages público das adaptações.

## Tamanho e limites (proposta)

| Parâmetro | Proposta | Limite |
| --- | --- | --- |
| Turma | 8–12 pessoas | Máximo 15. Acima disso não é “acompanhado” |
| Perfil | Já programam (Node ou Python) | Sem turma iniciante neste protocolo |
| Duração | 4 semanas de contacto + 1 de encerramento | Não comprime 240 h; é recorte |
| Recorte mínimo | M01 C01.1–C01.2 **ou** o módulo âncora da turma + 1 lab offline | Não promete M01–M09 completos |
| Instrutores | 1 docente + 1 monitor | Sem monitor, reduzir para 8 pessoas |
| Canais | LMS da instituição + clone Git | Sem WhatsApp improvisado como evidência |
| Gasto | Zero neste protocolo | Sem compra de GPU, domínio, Pages pago, API paga obrigatória |

Chaves **opcionais** (OpenRouter `:free`, Groq, AI Studio) ficam a cargo da instituição. Labs que exigem chave entram como **bloqueados** na [matriz](./matriz-prontidao.md), não como “integração real”.

## Semana 0 — diagnóstico (antes da aula 1)

1. Consentimento informado ([modelo no formulário](./formulario-resultados.md)). Sem consentimento, a pessoa estuda mas **não** entra nas métricas.
2. Ficha anónima de ambiente: SO, Node, Python, Docker, Chrome, WSL.
3. [Pré-teste](./pre-pos-teste.md) (os mesmos itens do pós-teste).
4. Canário técnico do instrutor (não do aluno): `npm test --prefix curso/preview`, `node --test curso/avaliacao-colaboracao/verificar.test.mjs`, `node curso/piloto/smoke-labs.mjs`.

## Recorte de 4 semanas (acompanhado)

| Semana | Objectivo | Tarefa do aluno | Aceite |
| --- | --- | --- | --- |
| 1 | Preview + M01 mínimo | Abrir o preview local; C01.1 (`exemplo-00` ou e-commerce :3000) | Print/log + pasta que existe |
| 2 | Um lab de API **ou** MCP **sem** fingir chave | C02.1 no lab 02 (LangGraph **sem** LLM) **ou** C03 documentado como bloqueado se faltar Inspector | Comando reproduzível no README da entrega |
| 3 | Decisão HITL / PII | C-COLAB T2 sozinho+colaborativo **ou** parágrafo HITL do M04 se a turma já chegou lá | `verificar.mjs` no JSON do aluno; vazamento = reprovado (não média 8,7) |
| 4 | Encerramento | Pós-teste; [formulário](./formulario-resultados.md) anónimo; 1 página “o que quebrou no meu setup” | Sem dados pessoais no Git |

Quem já está em M07–M09: no lugar da semana 2, rode o Monte Carlo (script, não chat) **ou** a decision tool do M09 (CPU, sem treino).

## Observação em sala (qualitativa)

O monitor anota **incidentes de setup**, não notas inventadas:

- Preview abriu? Recarga de `#/modulos/01.md` manteve CSS?
- PDF da Atividade abriu como PDF (não JSON)?
- Aluno tentou o `-z` antes do template?
- Legenda VTT visível no player? (não avaliar se “gostou da voz”)

## Acessibilidade no piloto

- Skip link, menu por teclado, Escape fecha o menu: testados no e2e quando o Chrome está presente.
- Narração: MP3 + VTT no disco. **Não** afirmamos ter ouvido o áudio. HeyGen fora do Git: sem transcrição aqui — oferecer o `aula.md` como alternativa.
- Não exigir Prompt API do Chrome como única via (C01.2 já aceita fallback documentado).

## Coleta consentida / anónima

- IDs: código aleatório gerado pelo aluno (`P-` + 4 dígitos). Sem nome no ficheiro de resultados.
- Proibido colar CPF, e-mail, prints de tela com rostos, logs com chave.
- Dados ficam no LMS da instituição, **não** neste repositório.

## O que este protocolo não faz

- Não declara reprodução oficial do CIB / arXiv:2611.02633v1.
- Não valida que “a turma aprendeu”.
- Não autoriza publicação pública das adaptações.
- Não contacta alunos.

Go / no-go: [criterios-go-nogo.md](./criterios-go-nogo.md).
