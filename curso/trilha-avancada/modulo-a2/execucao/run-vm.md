# Corrida real — A2 (VM de autoria)

Nada abaixo foi inventado. Pesos do SmolLM2-135M já estavam no cache Hugging Face desta VM (download feito na sessão de autoria, minutos antes). A parede do lab **não** inclui o download inicial (~270 MB).

## Hardware e software

```
utc 2026-11-12T13:39:35Z
uname Linux 6.12.113+ x86_64
cpu Intel(R) Xeon(R) Processor
nproc 4
MemTotal:       16387328 kB
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
pytest 9.2.0
```

JSON gerado: [`ca2-autoria.json`](./ca2-autoria.json) (cópia de `saidas/ca2.json` desta corrida).

## `python modulo-a2/lab/exemplo_numerico.py`

`elapsed_sec=1.190`  `exit=0`

```
QK^T
 tensor([[1., 1.],
        [0., 1.]])
QK^T / sqrt(2)
 tensor([[0.70710677, 0.70710677],
        [0.00000000, 0.70710677]])
pesos (softmax causal)
 tensor([[1.00000000, 0.00000000],
        [0.33023846, 0.66976154]])
saída nossa
 tensor([[1.00000000, 2.00000000],
        [2.33952284, 3.33952308]])
saída F.scaled_dot_product_attention
 tensor([[1.00000000, 2.00000000],
        [2.33952308, 3.33952308]])
delta máximo: 2.384185791015625e-07
LayerNorm([1,2,3]) tensor([-1.22473562,  0.00000000,  1.22473562]) média 2.0 desvio 0.8165027499198914
RMSNorm([1,2,3]) tensor([0.46290955, 0.92581910, 1.38872862])
```

## `python modulo-a2/lab/lab_a2.py`

`elapsed_sec=3.989`  `exit=0`  (`a2_2.segundos=2.754`, `segundos_total=2.76` medidos *dentro* do script)

```
=== Lab A2.1 — atenção do zero ===
  Δ máx vs SDPA = 2.384e-07  (limiar 1e-05)  causal_ok=True
=== Lab A2.2 — modelo real ===
  modelo: HuggingFaceTB/SmolLM2-135M
  camadas=30  d=576  Q=9 KV=3  GQA=True  act=silu  rope_θ=100000
  parâmetros: 134515008 (HF 134515008)  erro relativo=0.000e+00
  por componente: {'embedding': 28311552, 'atencao': 26542080, 'ffn': 79626240, 'norm': 35136, 'lm_head': 0, 'outros': 0}
  bloco 0 reconstruído: Δmáx=0.000e+00  Δmédia=0.000e+00  Δatenção=0.000e+00
  tokens: ['Seg', 'ur', 'ado', ':', 'ĠAna', 'ĠSou', 'za', '.', 'ĠPl', 'aca', ':', 'ĠABC', '-', '1', 'D', '2', '3', '.']
```

Mapa ASCII (camada 0, cabeça 0) — ver stdout completa no JSON (`ascii_cabeca0`). Triangular superior = 0 (causal_ok=true).

## `python -m pytest modulo-a2/testes -q --tb=short`

`elapsed_sec=4.115`  `exit=0`

```
...................                                                      [100%]
```

19 testes (15 sem modelo + 4 com `HuggingFaceTB/SmolLM2-135M`).

## Limitações desta corrida

- CPU only; T4/Colab não foi usada.
- Qwen2.5-0.5B **não** foi baixado (opcional via `TRILHA_A2_MODELO`).
- Download inicial do SmolLM2 não entra nos 3,99 s do lab.
- `lm_head=0` na tabela porque `tie_word_embeddings=true` (peso já no balde `embedding`).
