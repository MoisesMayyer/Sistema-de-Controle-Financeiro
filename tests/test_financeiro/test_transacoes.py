import pytest

from unittest.mock import patch

from financeiro.transacoes.crud import (
    adicionar_transacao,
    remover_transacao,
    editar_transacao,
    buscar_transacao,
    buscar_nome_categoria
)


@pytest.fixture
def mock_carregar_transacao(mock_transacoes):
    with patch(
        "financeiro.transacoes.crud.carregar_json",
        return_value=mock_transacoes
    ):
        yield


@pytest.fixture
def mock_carregar_categorias(mock_categorias):
    with patch(
        "financeiro.transacoes.crud.carregar_json",
        return_value=mock_categorias
    ):
        yield


@pytest.fixture
def mock_adicionar_transacao(mock_transacoes, mock_categorias):
    with patch(
        "financeiro.transacoes.crud.carregar_json",
        return_value=mock_transacoes
    ), patch(
        "financeiro.categorias.crud.carregar_json",
        return_value=mock_categorias
    ):
        yield


@pytest.mark.parametrize(
    "descricao, valor, tipo, categoria_id, data, resultado_esperado",
    [
        ("test1", 1, "despesa", 2, "12/12/2026", True),
        ("test2", 10, "despesa", 1, "12/12/2026", True),
        ("test3", 100, "despesa", None, "12/12/2026", True),
        ("test4", 1000, "receita", None, "12/12/2026", True),
        ("test5", 500, "despesa", 999, "12/12/2026", False),
    ]
)
def test_adicionar_transacao(
    mock_adicionar_transacao,
    descricao,
    valor,
    tipo,
    categoria_id,
    data,
    resultado_esperado
):
    resultado = adicionar_transacao(
        descricao,
        valor,
        tipo,
        categoria_id,
        data
    )

    assert resultado is resultado_esperado


def test_adicionar_transacao_cria_transacao(mock_adicionar_transacao,mock_transacoes):
    adicionar_transacao(
        "teste",
        50,
        "despesa",
        1,
        "12/12/2026"
    )

    transacao = mock_transacoes[-1]

    assert transacao["descricao"] == "teste"
    assert transacao["valor"] == 50
    assert transacao["tipo"] == "despesa"
    assert transacao["categoria_id"] == 1
    assert transacao["data"] == "12/12/2026"


@pytest.mark.parametrize(
    "id_transacao, resultado_esperado",
    [
        (1, True),
        (0, False),
        (999, False),
    ]
)
def test_remover_transacao(mock_carregar_transacao,id_transacao,resultado_esperado):
    sucesso = remover_transacao(id_transacao)

    assert sucesso is resultado_esperado


def test_remover_transacao_remove_id(mock_carregar_transacao,mock_transacoes):
    remover_transacao(1)

    assert all(
        transacao["id"] != 1
        for transacao in mock_transacoes
    )


@pytest.mark.parametrize(
    "id_editar, resultado_esperado",
    [
        (1, True),
        (2, True),
        (999, False),
    ]
)
def test_editar_transacao(mock_carregar_transacao,id_editar,resultado_esperado):
    resultado = editar_transacao(
        id_editar,
        "nova descricao",
        100,
        "despesa",
        1,
        "20/12/2026"
    )

    assert resultado is resultado_esperado


def test_editar_transacao_altera_dados(mock_carregar_transacao,mock_transacoes):

    editar_transacao(
        1,
        "nova descricao",
        500,
        "receita",
        None,
        "20/12/2026"
    )

    transacao = mock_transacoes[0]

    assert transacao["descricao"] == "nova descricao"
    assert transacao["valor"] == 500
    assert transacao["tipo"] == "receita"
    assert transacao["categoria_id"] is None
    assert transacao["data"] == "20/12/2026"


@pytest.mark.parametrize(
    "id_transacao, resultado_esperado",
    [
        (1, True),
        (999, False),
    ]
)
def test_buscar_transacao(mock_carregar_transacao,mock_transacoes,id_transacao,resultado_esperado):

    resultado = buscar_transacao(id_transacao)

    if resultado_esperado:
        assert resultado == mock_transacoes[0]
    else:
        assert resultado is None


@pytest.mark.parametrize(
    "categoria_id, resultado_esperado",
    [
        (1, "mercado"),
        (999, "Sem categoria"),
        (None, "Sem categoria"),
    ]
)
def test_buscar_nome_categoria(mock_carregar_categorias,categoria_id,resultado_esperado):

    resultado = buscar_nome_categoria(categoria_id)

    assert resultado == resultado_esperado