import pytest

@pytest.fixture
def mock_transacoes():
    return [
        {
            "id": 1,
            "descricao": "teste_1",
            "valor": 5.0,
            "tipo": "despesa",
            "categoria_id": 1,
            "data": "12/12/2026",
        },
        {
            "id": 2,
            "descricao": "teste_2",
            "valor": 10.0,
            "tipo": "despesa",
            "categoria_id": 2,
            "data": "12/12/2026",
        },
        {
            "id": 3,
            "descricao": "teste_3",
            "valor": 1000.0,
            "tipo": "receita",
            "categoria_id": None,
            "data": "12/12/2026",
        },
        {
            "id": 4,
            "descricao": "teste_4",
            "valor": 50.0,
            "tipo": "receita",
            "categoria_id": None,
            "data": "12/12/2026",
        },
    ]

@pytest.fixture
def mock_categorias():
    return [
    {
        "id": 1,
        "nome": "mercado",
        "limite": 800.0
    },
    {
        "id": 2,
        "nome": "computador",
        "limite": 1200.0
    },
    {
        "id": 3,
        "nome": "outros",
        "limite": 500.0
    }
]