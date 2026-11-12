"""Textos originais da trilha (espírito Amplitude + código). Não copiam os JSONL do M09."""

DOMINIOS: dict[str, list[str]] = {
    "auto": [
        "Segurado: Ana Souza. Placa: ABC-1D23. Reparo de lataria na porta dianteira.",
        "Orcamento de oficina: troca de para-choque. Valor: R$ 1250,00.",
        "Sinistro de colisao traseira no estacionamento. Vidro intacto.",
        "Funilaria e pintura no para-lama esquerdo. Data do atendimento: 12/11/2026.",
    ],
    "saude": [
        "Beneficiario: Ana Souza. Procedimento: consulta geriatrica. Valor: R$ 320,00.",
        "Guia de exames: hemograma completo e glicemia de jejum.",
        "Internacao de 2 diarias em quarto semi-privativo. Alta prevista amanha.",
        "Receituario de fisioterapia: 10 sessoes para reabilitacao de joelho.",
    ],
    "codigo": [
        "def tokenizar(texto: str) -> list[int]:\n    return tokenizer.encode(texto)",
        "for expert_id, peso in zip(top_idx, gates):\n    y += peso * experts[expert_id](x)",
        "assert num_experts_per_tok <= num_local_experts",
        "model.generate(input_ids, use_cache=True, max_new_tokens=16)",
    ],
}

PPL_CALIBRACAO: list[str] = [
    "A placa ABC-1D23 pertence a Ana Souza.",
    "O valor do reparo e 1250 reais com centavos em 00.",
    "Consulta geriatrica agendada para o beneficiario.",
    "O router escolhe dois experts por token.",
    "Quantizar pesos para inteiro reduz memoria em disco.",
    "A cache de chaves e valores evita recomputar o prefixo.",
    "O decimal 1250,00 nao deve virar 125000 depois da quantizacao.",
    "Mixture of experts nao e o mesmo que um time de agentes.",
    "LayerNorm normaliza features; RMSNorm nao subtrai a media.",
    "O LoRA do M09 atualiza q_proj e v_proj com matrizes finas.",
    "Um modelo denso de 1B ativa todos os parametros em cada token.",
    "Um MoE 1B-A400M ativa cerca de 400 milhoes por token.",
    "Batching junta sequencias; continuous batching troca no meio.",
    "PTQ depois do treino; QAT finge a quantizacao durante o treino.",
    "O servidor vLLM nao roda nesta CPU; fica como leitura.",
    "Greedy com temperatura zero deveria repetir o mesmo token.",
]


def frases_dominio(nome: str) -> list[str]:
    return list(DOMINIOS[nome])


def corpus_ppl() -> list[str]:
    return list(PPL_CALIBRACAO)
