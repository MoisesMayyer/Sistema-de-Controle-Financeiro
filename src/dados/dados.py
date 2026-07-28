import json
from pathlib import Path

PASTA_DADOS = Path(__file__).parent

CAMINHO_TRANSACOES  = PASTA_DADOS / "gastos.json"

CAMINHO_CATEGORIAS = PASTA_DADOS / "categorias.json"

CAMINHO_METAS = PASTA_DADOS / "metas.json"


def carregar_json(caminho: Path):

    if not caminho.exists():
        return []

    try:
        with open(caminho, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return []


def salvar_json(caminho: Path, dados):

    with open(caminho, "w", encoding="utf-8") as file:
        json.dump(
            dados,
            file,
            indent=4,
            ensure_ascii=False
        )