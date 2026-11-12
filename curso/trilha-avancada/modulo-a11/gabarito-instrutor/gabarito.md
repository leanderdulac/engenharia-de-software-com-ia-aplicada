# Gabarito A11 (instrutor)

Preenchido com a corrida real da VM de autoria. Se o aluno rodar outro `transformers` / outra CPU, **os limiares do checkpoint mandam**, não estes números literais.

O exemplo 2×3 da aula (logits `[2,0,-1]` / `[2,0.5,-1]`) é pedagogia, não item secreto de CA11. O aluno já o vê em `aula.md` e em `exemplo_numerico_aula()`.

## Ambiente da autoria

Ver [`../execucao/run-vm.md`](../execucao/run-vm.md). CPU, sem CUDA, torch 2.15.0+cpu, transformers 5.22.2, corrida 2026-11-12T13:48:19Z, `segundos_total=54.712`.

| Item | Medido na autoria | Limiar do aluno |
| --- | --- | --- |
| A11.1 `f_max` sem aux | **1.0** (expert 0 no top-2 de todos os tokens) | `colapso_sem_aux=true` (≥ 0,50) |
| A11.1 `f_max` com aux | **0.4785** | menor que o sem aux |
| A11.1 entropia sem → com | 1.356 → 2.026 | `mais_equilibrado_com_aux=true` |
| A11.1 params | total 33800, ativos/token 8648, k=2/8 | ativos < total |
| A11.1 `exemplo_aula.aux` | 2.8783159255981445 | > 0, `sum(f)=2` |
| A11.1 MSE sem / com aux | 1.79×10⁻⁴ / 4.51×10⁻⁴ | aux pode piorar MSE |
| A11.2 Granite | `status=ok`, 32 experts, top-8, **1334628352** params | config 32/8; pesos opcionais |
| A11.2 OLMoE | config 64/8, `nao_calibrado_cpu_7b` | não carregar 7B |
| A11.2 L1 Auto–Saúde | **0.0521** | — |
| A11.2 L1 Auto–Saúde permutado | **0.2005** | — |
| A11.2 `especializacao_aparente` | **false** | false é válido |
| A11.3 | `nao_executado` | obrigatório neste PR |
| A11.4 PPL fp32 / INT8+lm_head / INT8 sem lm_head / INT4 | 217.50 / **1060.79** / **950.45** / 506.19 | finitas; cabeça piora; INT4 fake ≠ INT8 real |
| A11.4 bytes fp32 → INT8 → INT8 sem cabeça | 538 060 288 → 145 237 536 → 117 478 940 | INT8 menor |
| A11.4 latência 8 tok | 0.167 / 0.109 / 0.116 / 0.160 s | INT4 fake não acelera |
| A11.5 MSE fp32 / PTQ / QAT | 1.38×10⁻⁴ / 1.89×10⁻⁴ / 3.65×10⁻⁴ | `qat_melhor_que_ptq=false` nesta semente |
| A11.6 Δ attn cache vs full | **2.384e-07** | < 1e-5 |
| A11.6 `generate` cache on/off | 0.164 s / 0.253 s (razão 1.54) | `cache_mais_rapido` pode ser false no aluno |
| A11.6 batch 1/4/8 tok/s | 786 / 1475 / 1542 | três chaves |
| vLLM / llama-server / GGUF / bnb / OLMoE pesos | `nao_calibrado*` | não inventar |

Observação do histograma Granite (camada agregada, 118+106+92 tokens): os três domínios usam os mesmos experts “populares” (índices altos ~31, 13, 8…). Permutar Saúde **aumenta** a L1 porque quebra esse perfil compartilhado. Um parágrafo de aluno que diga “não apareceu especialização nesta amostra” está correto. Um que invente “o expert 7 é funilaria” está errado.

INT8 PPL > INT4 PPL tem **duas** causas, ambas no JSON:

1. `int8_dinamico` inclui `lm_head` (1061) vs `int8_dinamico_sem_lm_head` (950). Quantizar a cabeça dói.
2. Mesmo sem cabeça, 950 > 506 do INT4 **fake-quant** (compute fp32). Não é evidência de que 4 bits “ganham” de 8.

Parágrafo de aluno que só diz “INT8 é pior” sem citar o campo `sem_lm_head` fica no teto 8.

## Como conferir um `ca11.json` entregue

1. Abrir o JSON. Se `ambiente.epoch_unix` for idêntico ao de outro aluno byte a byte **e** os histogramas `f_final` também, pedir reexecução (semente do brinquedo é fixa — o epoch_unix e o `segundos_*` têm de mudar).
2. Checar as flags / limiares de [`../checkpoint-ca11.md`](../checkpoint-ca11.md).
3. `a11_3_lora_moe.status` tem de ser `nao_executado` enquanto A6 não existir. LoRA-MoE inventado = 0 nesse item.
4. Campos `nao_calibrado`: se o aluno preencheu um throughput de vLLM sem GPU no `ambiente`, zerar honestidade.
5. Parágrafo: tem de citar números que existem no JSON (PPL, L1 ou `erro` de `nao_coube`, razão cache).

## Erros comuns

| Sintoma | Causa típica | Não faça |
| --- | --- | --- |
| `colapso_sem_aux=false` | tirou `vies_expert0` | não revele 2.5; pergunte se o router começa simétrico |
| PPL INT4 ≪ fp32 | copiou pesos errados / corpus de 1 token | peça `n_frases_ppl` |
| bytes INT8 ≥ fp32 | `nbytes_estado` sem packed params | o lab já conta `weight()`; se o aluno reimplementou, peça o código |
| Δ attn ≥ 1e-5 | `causal=True` no passo com K concatenado até t, ou comparou posições futuras | peça o recorte `0..t` |
| “vLLM 2–4×” | abstract do paper Kwon | `nao_calibrado_cpu` |
| especialização true com L1 real < permutado | inverteu a desigualdade | leia `especializacao_aparente` |

## Testes

```bash
cd curso/trilha-avancada
python -m pytest modulo-a11/testes -q
python -m pytest modulo-a11/testes -q -m "not modelo"
```

Autoria: **11** testes, exit 0 (10 sem modelo + 1 `modelo` com SmolLM2). Há `DeprecationWarning` de `torch.ao.quantization` — esperado, documentado na aula.

## Números do exemplo 2×3 (iguais à aula)

```
probs token0 ≈ [0.84379470, 0.11419519, 0.04201007]
gates token0 ≈ [0.88079703, 0.11920291]
f = [1, 1, 0]
aux ≈ 2.87831593
```
