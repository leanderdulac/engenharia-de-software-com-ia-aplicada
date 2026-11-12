"""Pares chosen/rejected originais no espírito Amplitude. Não copiam o JSONL do M09.

Padrão que o M09 ensinou (schema, harness, vírgula decimal) reconstruído com nomes
sintéticos já usados no A2/A11 (`Ana Souza` / `ABC-1D23`). O arquivo
``preference-dataset-amplitude.jsonl`` **não** é lido nem republicado.

Prompts terminam em ``\\n`` (um só) para o tokenizer do SmolLM2 não fundir o
último token do prompt com o primeiro da compleção. Compleções **não** começam
com newline. Treino e avaliação têm prompts disjuntos.
"""

from __future__ import annotations

from typing import Any


def _p(texto: str) -> str:
    """Fecha o prompt num limite de token estável (newline simples, não ``\\n\\n``)."""
    return texto.rstrip("\n") + "\n"


def pares_treino() -> list[dict[str, str]]:
    return [
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Segurado: Ana Souza. Placa: ABC-1D23. Valor: R$ 1250,00."
            ),
            "chosen": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":1250.00}',
            "rejected": (
                "Com base no texto, a segurada e Ana Souza, a placa e ABC-1D23 e o valor "
                "total do reparo e R$ 1.250,00 (por extenso, sem JSON)."
            ),
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Segurado: Ana Souza. Placa: ABC-1D23. Valor: R$ 1250,00. "
                "Use ponto no valor."
            ),
            "chosen": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":1250.00}',
            "rejected": '{"segurado":"Ana Souza","placa":"ABC-1D23","valor":125000}',
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Orcamento: troca de para-choque. Segurado: Bruno Lima. Placa: KLM-4401. Valor: R$ 980,50."
            ),
            "chosen": '{"segurado":"Bruno Lima","placa":"KLM-4401","valor":980.50}',
            "rejected": '{"nome":"Bruno Lima","veiculo":"KLM-4401","preco":"980,50"}',
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Sinistro de lataria. Segurado: Carla Dias. Placa: RST-7788. Valor: R$ 320,00."
            ),
            "chosen": '{"segurado":"Carla Dias","placa":"RST-7788","valor":320.00}',
            "rejected": '{"segurado":"Carla Dias","placa":"RST-7788"}',
        },
        {
            "prompt": _p(
                "Responda so o JSON pedido.\n\n"
                "Segurado: Diego Alves. Placa: FGH-2210. Valor: R$ 4100,00."
            ),
            "chosen": '{"segurado":"Diego Alves","placa":"FGH-2210","valor":4100.00}',
            "rejected": (
                "Claro! Vou te ajudar. Primeiro notei o nome Diego Alves, depois a placa "
                "FGH-2210, e por fim o valor quatro mil e cem reais. Espero ter ajudado :)"
            ),
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves beneficiario, procedimento, valor.\n\n"
                "Beneficiario: Ana Souza. Procedimento: consulta geriatrica. Valor: R$ 320,00."
            ),
            "chosen": '{"beneficiario":"Ana Souza","procedimento":"consulta geriatrica","valor":320.00}',
            "rejected": "A paciente Ana Souza fez uma consulta. O valor ficou em trezentos e vinte reais.",
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves beneficiario, procedimento, valor.\n\n"
                "Guia: hemograma. Beneficiario: Elisa Prado. Valor: R$ 85,90."
            ),
            "chosen": '{"beneficiario":"Elisa Prado","procedimento":"hemograma","valor":85.90}',
            "rejected": '{"beneficiario":"Elisa Prado","procedimento":"hemograma","valor":8590}',
        },
        {
            "prompt": _p("O que e Mixture of Experts, em uma frase, sem chamar de time de agentes."),
            "chosen": "MoE e um FFN com N experts e um router que ativa k deles por token.",
            "rejected": "MoE e um time de agentes que conversam entre si para dividir o trabalho.",
        },
        {
            "prompt": _p("No LoRA do M09, o que q_proj e v_proj sao?"),
            "chosen": "Matrizes de projecao da atencao: consulta e valor.",
            "rejected": "Dois hiperparametros de temperature e top-k no sampler.",
        },
        {
            "prompt": _p("PTQ acontece quando?"),
            "chosen": "Depois do treino, calibrando escalas nos pesos ja prontos.",
            "rejected": "Durante o treino, com straight-through estimator no round.",
        },
    ]


def pares_avaliacao() -> list[dict[str, str]]:
    """Hold-out: prompts que **nao** aparecem no treino."""
    return [
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Segurado: Fabio Nunes. Placa: XYZ-9900. Valor: R$ 1500,00."
            ),
            "chosen": '{"segurado":"Fabio Nunes","placa":"XYZ-9900","valor":1500.00}',
            "rejected": '{"segurado":"Fabio Nunes","placa":"XYZ-9900","valor":150000}',
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves segurado, placa, valor.\n\n"
                "Funilaria. Segurado: Helena Costa. Placa: QWE-1122. Valor: R$ 640,00."
            ),
            "chosen": '{"segurado":"Helena Costa","placa":"QWE-1122","valor":640.00}',
            "rejected": (
                "A segurada Helena Costa, placa QWE-1122, tem um orcamento de seiscentos "
                "e quarenta reais, sem JSON."
            ),
        },
        {
            "prompt": _p(
                "Extraia JSON com chaves beneficiario, procedimento, valor.\n\n"
                "Guia: raio-x. Beneficiario: Igor Pinto. Valor: R$ 210,00."
            ),
            "chosen": '{"beneficiario":"Igor Pinto","procedimento":"raio-x","valor":210.00}',
            "rejected": '{"beneficiario":"Igor Pinto","procedimento":"raio-x"}',
        },
        {
            "prompt": _p(
                "Devolva um JSON com chaves placa e ok. Placa ABC-1D23, ok verdadeiro."
            ),
            "chosen": '{"placa":"ABC-1D23","ok":true}',
            "rejected": "talvez, depende da oficina e do perito e de uma analise longa",
        },
    ]


def pares_dpo() -> list[dict[str, str]]:
    """Todos os pares (treino + eval). Formato TRL: prompt / chosen / rejected."""
    return pares_treino() + pares_avaliacao()


def pares_kto(pares: list[dict[str, str]] | None = None) -> list[dict[str, Any]]:
    """Converte cada par em dois exemplos KTO (label True/False)."""
    pares = pares if pares is not None else pares_treino()
    out: list[dict[str, Any]] = []
    for p in pares:
        out.append({"prompt": p["prompt"], "completion": p["chosen"], "label": True})
        out.append({"prompt": p["prompt"], "completion": p["rejected"], "label": False})
    return out


def split_ok() -> dict[str, Any]:
    tr, ev = pares_treino(), pares_avaliacao()
    pt = {p["prompt"] for p in tr}
    pe = {p["prompt"] for p in ev}
    return {
        "n_treino": len(tr),
        "n_eval": len(ev),
        "prompts_disjuntos": pt.isdisjoint(pe),
        "n_prompts_treino": len(pt),
        "n_prompts_eval": len(pe),
    }


def conferir_fronteira(tok, pares: list[dict[str, str]] | None = None) -> dict[str, Any]:
    """``tokenize(prompt)`` tem de ser prefixo de ``tokenize(prompt+compleção)``."""
    pares = pares or pares_dpo()
    falhas: list[dict[str, Any]] = []
    for i, ex in enumerate(pares):
        pid = tok(ex["prompt"], add_special_tokens=False).input_ids
        for lado in ("chosen", "rejected"):
            fid = tok(ex["prompt"] + ex[lado], add_special_tokens=False).input_ids
            if fid[: len(pid)] != pid:
                n = 0
                while n < len(pid) and n < len(fid) and pid[n] == fid[n]:
                    n += 1
                falhas.append(
                    {
                        "i": i,
                        "lado": lado,
                        "sobra": tok.decode(pid[n:]),
                    }
                )
    return {"n": len(pares), "n_falhas": len(falhas), "ok": len(falhas) == 0, "falhas": falhas}


def estatistica_comprimento(pares: list[dict[str, str]] | None = None) -> dict[str, Any]:
    pares = pares or pares_dpo()
    ch = [len(p["chosen"]) for p in pares]
    rj = [len(p["rejected"]) for p in pares]
    n = len(pares)
    return {
        "n": n,
        "chosen_chars_medio": sum(ch) / n,
        "rejected_chars_medio": sum(rj) / n,
        "razao_rejected_sobre_chosen": (sum(rj) / n) / max(sum(ch) / n, 1e-9),
        "rejeitado_mais_longo": sum(rj) / n > sum(ch) / n,
        "nota": (
            "rejeitados em prosa sao mais longos; DPO sem normalizar por |y| "
            "pode aprender 'seja curto', nao so 'seja JSON'"
        ),
    }
