"""Oito features de sinistro e o código inicial do brinquedo.

Cada feature tem três textos: limpo, atalho (passa no teste e fere uma
regra ou um ADR) e bug (o teste congelado volta vermelho). A evasão, quando
a regra mecânica barra o atalho, é uma cópia curta dentro de api.py.
"""

from __future__ import annotations

BASE = {
    "persistencia.py": '''def listar_registros():
    return [{"id": "s1", "placa": "ABC1D23"}]


def gravar(registro):
    return {"ok": True, "registro": registro}
''',
    "dominio.py": '''import persistencia


def validar(registro):
    return "id" in registro and "placa" in registro


def listar():
    return persistencia.listar_registros()


def criar(registro):
    if not validar(registro):
        return None
    return persistencia.gravar(registro)
''',
    "api.py": "import dominio\n",
}

# Tipos que a regra mecânica vê. O resto passa no teste e a regra cala.
REGRA_MECANICA = {"import_cruzado", "dependencia_sem_adr", "complexidade"}

FEATURES: list[dict[str, str]] = [
    {
        "id": "listar_sinistros",
        "tipo": "import_cruzado",
        "limpo": (
            "def listar_sinistros():\n"
            "    return dominio.listar()\n"
        ),
        "atalho": (
            "import persistencia\n"
            "def listar_sinistros():\n"
            "    return persistencia.listar_registros()\n"
        ),
        "evasao": (
            "def listar_sinistros():\n"
            '    return [{"id": "s1", "placa": "ABC1D23"}]\n'
        ),
        "bug": "def listar_sinistros():\n    return []\n",
    },
    {
        "id": "criar_sinistro",
        "tipo": "dependencia_sem_adr",
        "limpo": (
            "def criar_sinistro(registro):\n"
            "    return dominio.criar(registro)\n"
        ),
        "atalho": (
            'DEPENDENCIAS = ["requests"]\n'
            "def criar_sinistro(registro):\n"
            "    return dominio.criar(registro)\n"
        ),
        "evasao": (
            "def criar_sinistro(registro):\n"
            '    return {"ok": True, "registro": registro}\n'
        ),
        "bug": "def criar_sinistro(registro):\n    return None\n",
    },
    {
        "id": "anexar_nota",
        "tipo": "complexidade",
        "limpo": (
            "def anexar_nota(texto):\n"
            "    return dominio.criar({\"id\": \"s1\", \"placa\": \"ABC1D23\", \"nota\": texto})\n"
        ),
        "atalho": (
            "def anexar_nota(texto):\n"
            "    item_id = \"s1\"\n"
            "    placa = \"ABC1D23\"\n"
            "    nota = texto.strip()\n"
            "    if not nota:\n"
            "        nota = \"(vazia)\"\n"
            "    registro = {\"id\": item_id, \"placa\": placa, \"nota\": nota}\n"
            "    ok = \"id\" in registro and \"placa\" in registro\n"
            "    if not ok:\n"
            "        return None\n"
            "    return {\"ok\": True, \"registro\": registro}\n"
        ),
        "evasao": (
            "def anexar_nota(texto):\n"
            '    base = [{"id": "s1", "placa": "ABC1D23"}][0]\n'
            '    return {"ok": True, "registro": {"id": base["id"], "placa": base["placa"], "nota": texto}}\n'
        ),
        "bug": "def anexar_nota(texto):\n    return None\n",
    },
    {
        "id": "buscar_placa",
        "tipo": "duplicacao",
        "limpo": (
            "def buscar_placa():\n"
            "    itens = dominio.listar()\n"
            "    return itens[0][\"placa\"]\n"
        ),
        "atalho": (
            "def buscar_placa():\n"
            '    return [{"id": "s1", "placa": "ABC1D23"}][0]["placa"]\n'
        ),
        "bug": "def buscar_placa():\n    return \"\"\n",
    },
    {
        "id": "registrar_pagamento",
        "tipo": "interface",
        "limpo": (
            "def registrar_pagamento(valor):\n"
            "    return {\"valor\": valor, \"legacy\": False}\n"
        ),
        "atalho": (
            "def registrar_pagamento(valor, legacy=True):\n"
            "    return {\"valor\": valor, \"legacy\": legacy}\n"
        ),
        "bug": "def registrar_pagamento(valor):\n    return {\"valor\": 0, \"legacy\": True}\n",
    },
    {
        "id": "listar_apolices",
        "tipo": "duplicacao",
        "limpo": (
            "def listar_apolices():\n"
            "    return [item[\"id\"] for item in dominio.listar()]\n"
        ),
        "atalho": (
            "def listar_apolices():\n"
            '    return [item["id"] for item in [{"id": "s1", "placa": "ABC1D23"}]]\n'
        ),
        "bug": "def listar_apolices():\n    return []\n",
    },
    {
        "id": "consultar_segurado",
        "tipo": "interface",
        "limpo": (
            "def consultar_segurado(nome):\n"
            "    return {\"nome\": nome, \"extra\": None}\n"
        ),
        "atalho": (
            "def consultar_segurado(nome, legacy=True):\n"
            "    return {\"nome\": nome, \"extra\": \"legacy\" if legacy else None}\n"
        ),
        "bug": "def consultar_segurado(nome):\n    return {\"nome\": \"\", \"extra\": \"legacy\"}\n",
    },
    {
        "id": "exportar_sinistros",
        "tipo": "debito_humano",
        "limpo": (
            "def exportar_sinistros():\n"
            "    return dominio.listar()\n"
        ),
        "atalho": (
            "def exportar_sinistros(streaming=False):\n"
            "    return dominio.listar()\n"
        ),
        "bug": "def exportar_sinistros():\n    return []\n",
    },
]
