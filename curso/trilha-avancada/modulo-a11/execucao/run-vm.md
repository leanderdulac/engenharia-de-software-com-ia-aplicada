# Corrida real — A11 (VM de autoria)

Nada abaixo foi inventado. Pesos do SmolLM2-135M já estavam no cache (A2). Granite 3.1-1B-A400M-Instruct foi baixado nesta sessão (~1,3B, bf16 no Hub, carregado em fp32). A parede do lab **inclui** a carga do Granite (42,9 s de 54,7 s).

## Hardware e software

```
utc 2026-11-12T13:48:19Z
uname Linux 6.12.113+ x86_64
cpu Intel(R) Xeon(R) Processor
nproc 4
MemTotal:       16387328 kB
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
pytest 9.2.0
```

JSON gerado: [`ca11-autoria.json`](./ca11-autoria.json) (cópia de `saidas/ca11.json` desta corrida).

## `python modulo-a11/lab/lab_a11.py`

`elapsed_sec=56.747` (parede do processo)  `exit=0`  (`segundos_total=54.712` medidos *dentro* do script)

```
=== A11.1 MoE de brinquedo ===
E00 |████████████████████| 1.000
E01 |█████               | 0.258
E02 |                    | 0.000
E03 |██████              | 0.279
E04 |███████             | 0.344
E05 |                    | 0.000
E06 |                    | 0.000
E07 |██                  | 0.119
--- com aux ---
E00 |████████████████████| 0.479
E01 |██████████          | 0.236
E02 |███████████         | 0.252
E03 |█████████           | 0.225
E04 |████████            | 0.197
E05 |████████            | 0.186
E06 |████████            | 0.197
E07 |██████████          | 0.229
  f_max sem=1.000 com=0.479  colapso=True equilibrado=True
  params total=33800 ativos/token=8648 k=2/8
=== A11.2 Granite (ou config) ===
  granite status: ok experts 32 k 8
=== A11.5 QAT vs PTQ (MLP) ===
  mse fp32=0.0001 ptq=0.0002 qat=0.0004
=== A11.6 KV cache + batch (inclui prova MiniDecoder) ===
  cache on=0.164s off=0.253s  prova_attn_ok=True
=== A11.4 PTQ SmolLM2 ===
  ppl fp32=217.498 int8=1060.785 int4=506.192

JSON → modulo-a11/saidas/ca11.json  (54.712 s)
```

Granite: `num_parameters=1334628352`, `l1_auto_saude=0.0521`, `l1_auto_saude_permutado=0.2005`, `especializacao_aparente=false`. OLMoE: só config (64 experts / top-8).

PTQ bytes: fp32 538060288 → INT8 144905756. INT4 `bytes_empacotados_estimados=56401920` (fake-quant, 210 matrizes). `gguf_llama_cpp=nao_calibrado`, `bitsandbytes_llm_int8=nao_calibrado_cpu`.

Batch forward tok/s: 1→786, 4→1475, 8→1542. `vllm_continuous_batching=nao_calibrado_cpu`.

Há `UserWarning`/`DeprecationWarning` de `torch.ao.quantization` e `torch.quantize_per_tensor` — esperados no torch 2.15.

## `python -m pytest modulo-a11/testes -q --tb=short`

`elapsed_sec≈13.1`  `exit=0`

```
...........                                                              [100%]
```

11 testes (10 sem modelo + 1 com `HuggingFaceTB/SmolLM2-135M`). Sem modelo, ~6 s (`..........`).

## Limitações desta corrida

- CPU only; T4/Colab **não** foi usada.
- vLLM, llama-server, GGUF, bitsandbytes, NF4 runtime: **não calibrados**.
- OLMoE-1B-7B pesos **não** carregados (~7B bf16).
- CA11.3 LoRA-MoE **não executado** (A6 ausente).
- INT4 não acelera (compute fp32). INT8 PPL pior que INT4 neste recorte porque o dinâmico quantiza `lm_head`.
- QAT no MLP **não** ganhou do PTQ (400 passos, semente 0).
- Especialização Auto vs Saúde **não** apareceu (`especializacao_aparente=false`).
- Download inicial do Granite não está separado no `segundos_total`; a carga+forward do A11.2 levou 42,855 s.
