from unittest.mock import patch
import pytest

from financeiro.categorias.crud import (
    buscar_categoria,
    nova_categoria,
    editar_categoria,
    remover_categoria
)

@pytest.fixture
def mock_carregar_categorias(mock_categorias):

    with patch(
        "financeiro.categorias.crud.carregar_json",
        return_value=mock_categorias
    ):
        yield


@pytest.fixture
def mock_remover_categoria(mock_categorias, mock_transacoes):
    with patch(
        "financeiro.categorias.crud.carregar_json",
        side_effect=[mock_categorias, mock_transacoes]
    ):
        yield


def test_buscar_categorias(mock_carregar_categorias, mock_categorias):

    categoria = buscar_categoria(1)

    assert categoria == mock_categorias[0]


@pytest.mark.parametrize(
    "id_buscar, resultado_esperado",
    [
        (1, True),
        (2, True),
        (3, True),
        (999, False)
    ]
)
def test_retorno_buscar_categoria(mock_carregar_categorias, id_buscar, resultado_esperado):

    categoria = buscar_categoria(id_buscar)

    if resultado_esperado:
        assert categoria is not None
    else:
        assert categoria is None


def test_nova_categoria_retorno(mock_carregar_categorias, mock_categorias):

    resultado = nova_categoria("teste", 1000.0)

    assert resultado is True


def test_nova_categoria_criada(mock_carregar_categorias, mock_categorias):

    nova_categoria("teste2", 160.0)

    categoria= mock_categorias[-1]

    assert categoria["nome"] == "teste2"
    assert categoria["limite"] == 160.0
    assert categoria["id"] == 4


@pytest.mark.parametrize(
    "id_alterar, novo_nome, novo_valor, resultado_esperado",
    [
        (1, "teste_editado", 2000.0, True),
        (999, "teste_editado3", 4000.0, False),
    ]
)
def test_editar_categoria(mock_categorias,mock_carregar_categorias,id_alterar,novo_nome,novo_valor,resultado_esperado):

    resultado = editar_categoria(id_alterar, novo_nome, novo_valor)
    assert resultado is resultado_esperado


def test_editar_categoria_altera_dados(mock_categorias,mock_carregar_categorias):

    editar_categoria(1, "teste_editado2", 3000.0)

    categoria = mock_categorias[0]

    assert categoria["nome"] == "teste_editado2"
    assert categoria["limite"] == 3000.0
    assert categoria["id"] == 1


@pytest.mark.parametrize(
    "id_remover, resultado_esperado",
    [
        (1, False),
        (2, False),
        (3, True),
        (999, False),
    ]
)
def test_remover_categoria(mock_remover_categoria, mock_categorias, id_remover, resultado_esperado):
    remover = remover_categoria(id_remover)

    assert remover is resultado_esperado


def test_remover_categoria_remove_id(mock_remover_categoria, mock_categorias):
    remover_categoria(3)

    assert all(
        categoria["id"] != 3
        for categoria in mock_categorias
    )
