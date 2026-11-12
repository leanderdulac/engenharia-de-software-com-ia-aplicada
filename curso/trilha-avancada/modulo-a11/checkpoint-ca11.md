# CA11 — checkpoint objetivo (aluno)

Prática **opcional** da trilha. Não substitui C01–C09. Não vale para a média das 240 h salvo o regulamento da turma decidir depois.

Entregue um único pacote:

1. `saidas/ca11.json` gerado por `python modulo-a11/lab/lab_a11.py` **na sua máquina** (ou Colab). Não reescreva os números à mão.
2. Um parágrafo (máx. 1 página) apontando campos do JSON. Sem print sem arquivo.

O gabarito do instrutor **não** faz parte desta entrega. Se você abriu `gabarito-instrutor/`, declare.

CA11.3 **não é exigido**: A6 não foi publicado. O JSON deve trazer `a11_3_lora_moe.status = nao_executado`. Inventar um LoRA-MoE zera o item de honestidade.

## CA11.1 — MoE de brinquedo

| Critério | Campo | Limiar |
| --- | --- | --- |
| Colapso sem aux | `a11_1.comparacao.colapso_sem_aux` | **true** |
| Aux equilibra | `a11_1.comparacao.mais_equilibrado_com_aux` | **true** |
| 8 experts, top-2 | `a11_1.comparacao.sem_aux.parametros` | `n_experts=8`, `k=2`, ativos < totais |
| Exemplo da aula | `a11_1.exemplo_aula.aux` | finito e > 0; `sum(f)=2` |
| Testes sem modelo | `pytest modulo-a11/testes -q -m "not modelo"` | todos passam |

O viés no expert 0 (`vies_expert0=2.5`) é proposital. Não “conserte” tirando o viés para o colapso desaparecer.

## CA11.2 — MoE real (config sempre; pesos se couber)

Modelo padrão: `ibm-granite/granite-3.1-1b-a400m-instruct`. OLMoE é só card/config nesta CPU.

| Critério | Campo | Limiar |
| --- | --- | --- |
| Granite 32 experts, top-8 | `a11_2.config_granite` | `num_local_experts=32`, `num_experts_per_tok=8` |
| OLMoE lido | `a11_2.config_olmoe_somente_card` | 64 experts, top-8; `olmoe_status` contém `nao_calibrado` |
| Pesos | `a11_2.status` | `ok` **ou** `nao_coube` / `pulado_env` com `erro` preenchido |
| Se `ok` | `uso_por_dominio`, `l1_auto_saude`, `l1_auto_saude_permutado` | presentes; especialização pode ser **false** |

Parágrafo: se `ok`, compare L1 real vs permutado com os números do JSON. Se `nao_coube`, cite o `erro` e a config — não invente histograma.

## CA11.4 — PTQ no SmolLM2

Âncora enquanto A5 não existe. Corpus = `lab/frases.py` (original).

| Critério | Campo | Limiar |
| --- | --- | --- |
| Três PPL finitas | `a11_4.fp32.ppl`, `int8_dinamico.ppl`, `int4_grupo64_fake.ppl` | > 1 e < inf |
| Bytes | `fp32.bytes` vs `int8_dinamico.bytes` | INT8 **menor** que fp32 |
| INT4 é fake | `a11_4.int4_grupo64_fake.nota` | declara compute em fp32 |
| Não calibrados | `gguf_llama_cpp`, `bitsandbytes_llm_int8` | `nao_calibrado*` |
| Testes com modelo | `pytest -q` (marca `modelo`) | passam |

Não substitua GGUF/NF4 por um número “típico da internet”.

## CA11.5 — QAT vs PTQ (MLP)

| Critério | Campo | Limiar |
| --- | --- | --- |
| Três MSE | `a11_5.mse_fp32`, `mse_ptq_depois`, `mse_qat` | finitos; fp32 ≤ PTQ (folga 1e-6) |
| Flags | `ptq_pior_que_fp32` | true ou empate numérico declarado |

`qat_melhor_que_ptq` **pode** falhar em semente azarada; o parágrafo diz o que o JSON mostrou.

## CA11.6 — KV cache e batch

| Critério | Campo | Limiar |
| --- | --- | --- |
| Prova de atenção | `a11_6.prova_minidecoder.cache_attn_ok` | **true** (Δ < 1e-5) |
| Ids greedy iguais | `prova_minidecoder.greedy_ids_iguais` | **true** |
| Medição real | `generate_use_cache_true_s` e `_false_s` | ambos > 0 |
| Servidores | `vllm_continuous_batching`, `llama_server` | `nao_calibrado*` |
| Batch 1/4/8 | `batch_forward` | três chaves com `tokens_por_s` |

Se `cache_mais_rapido` for false em CPU, **declare**. Inventar speedup zera.

## Rubrica rápida (0–10, só CA11)

| Nota | Evidência |
| --- | --- |
| 9–10 | JSON reproduzível; CA11.1 flags; config 32/8; PTQ com três PPL; prova de cache; parágrafo honesto sobre CA11.3 e `nao_calibrado` |
| 7–8 | Limiares ok; parágrafo vago ou Granite pulado sem citar o `erro` |
| 5–6 | JSON de outra pessoa / números digitados; PPL inventada; vLLM “medido” sem campo no JSON |
| 0–4 | Sem JSON; colapso forçado no editor; gabarito colado como medição |

Mesma regra do M09 e do CA2: hardware diferente → declare versões e o que faltou. Inventar 0.0 zera o checkpoint.
