"""Frases originais no espírito Amplitude vs fora do domínio. Não leem o JSONL do M09."""

from __future__ import annotations

# 1 = sinistro / segurado / placa (domínio do curso); 0 = outro (código, clima, receita)
TREINO: list[tuple[str, int]] = [
    ("Segurado Ana Souza, placa ABC-1D23, valor do reparo 1250 reais.", 1),
    ("Orcamento de funilaria no para-lama. Sinistro de colisao traseira.", 1),
    ("A placa KLM-4401 pertence a Bruno Lima. Vidro intacto.", 1),
    ("Guia de sinistro: troca de para-choque e pintura na porta.", 1),
    ("Segurada Carla Dias, placa XYZ-9988, 3200 reais de lataria.", 1),
    ("Valor do conserto com centavos: R$ 980,50. Oficina credenciada.", 1),
    ("Atendimento de auto: Diego Alves, placa FGH-1010, 75,90.", 1),
    ("Colisao no estacionamento. Segurado pede reembolso da funilaria.", 1),
    ("def tokenizar(texto): return tokenizer.encode(texto)", 0),
    ("O router escolhe dois experts por token no MoE.", 0),
    ("LayerNorm normaliza features; RMSNorm nao subtrai a media.", 0),
    ("Receituario de fisioterapia: dez sessoes para o joelho.", 0),
    ("Consulta geriatrica agendada. Hemograma e glicemia de jejum.", 0),
    ("A cache KV evita recomputar o prefixo na geracao.", 0),
    ("Choveu granizo em novembro. Temperatura maxima de 18 graus.", 0),
    ("O batch junta sequencias; continuous batching troca no meio.", 0),
]

EVAL: list[tuple[str, int]] = [
    ("Segurado Eva Martins, placa RST-2222, sinistro de 410 reais.", 1),
    ("Fabio Nunes informa placa UWW-7777 e orcamento de funilaria.", 1),
    ("Reparo de lataria na porta dianteira. Valor com ponto decimal.", 1),
    ("model.generate(input_ids, use_cache=True, max_new_tokens=16)", 0),
    ("Internacao de duas diarias em quarto semi-privativo.", 0),
    ("Quantizar pesos para inteiro reduz memoria em disco.", 0),
]


def split_ok() -> bool:
    a = {t for t, _ in TREINO}
    b = {t for t, _ in EVAL}
    return a.isdisjoint(b) and len(TREINO) >= 8 and len(EVAL) >= 4


def xy(pares: list[tuple[str, int]]) -> tuple[list[str], list[int]]:
    textos, y = zip(*pares)
    return list(textos), list(y)
