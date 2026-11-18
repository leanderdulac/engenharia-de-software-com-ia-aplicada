# Corrida real — A0 (VM de autoria)

```
utc 2026-11-12T14:42:41Z
python 3.12.3
torch 2.15.0+cpu  cuda False
transformers 5.22.2
peft 0.21.2
trl 1.17.1
```

JSON: [`ca0-autoria.json`](./ca0-autoria.json). `epoch_unix=1794494561`.

## `python modulo-a0/lab/lab_a0.py`

`segundos_total=9.864`

```
=== A0.1 bancada HuggingFaceTB/SmolLM2-135M n=20 seed=0 ===
  device=cpu gpu=None
  torch=2.15.0+cpu transformers=5.22.2
  corrida1 p50=0.172s p95=0.186s tok/s=46.01 rss_pico=993.1
  corrida2 p50=0.163s  repetivel_p50_±20%=True
```

## pytest

`python -m pytest modulo-a0/testes -q` — 4 testes (3 `not modelo` + 1 `modelo`).
