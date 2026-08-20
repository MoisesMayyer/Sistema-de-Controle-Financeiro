import pytest

from unittest.mock import patch

from financeiro.metas.crud import (
    calcular_porcentagem_meta,
    adicionar_meta,
    adicionar_valor_meta,
    remover_meta,
    editar_meta,
    buscar_meta_por_id)


@pytest.fixture
def mock_carregar_metas(mock_metas):
    with patch(
        "financeiro.metas.crud.carregar_json",
        return_value=mock_metas
    ):
        yield


@pytest.mark.parametrize(
    "valor_atual, valor_meta, resultado_esperado",
    [
        (600.0, 1200.0, 50.0),
        (0.0, 1000.0, 0.0),
        (900.0, 900.0, 100.0),
        (1500.0, 1000.0, 100.0),
        (500.0, 0.0, 0.0),
    ]
)
def test_calcular_porcentagem_meta(valor_atual, valor_meta, resultado_esperado):

    porcentagem_meta = calcular_porcentagem_meta(valor_atual, valor_meta)

    assert porcentagem_meta == resultado_esperado


@pytest.mark.parametrize(
    "nome_meta, valor_meta, resultado_esperado",
    [
        ("computador", 100.0, True),
        ("carro", 60000, True),
        ("tenis", 550.0, True),
    ]
)
def test_adicionar_meta(mock_carregar_metas, nome_meta, valor_meta, resultado_esperado):

    resultado_metas = adicionar_meta(nome_meta, valor_meta)

    assert resultado_metas == resultado_esperado


@pytest.mark.parametrize(
    "nome_meta, valor_meta",
    [
        ("viagem", 2000.0),
        ("curso", 1500.0),
        ("pao", 10.0),
    ]
)
def test_meta_adicionada(mock_carregar_metas, mock_metas, nome_meta, valor_meta):

    adicionar_meta(nome_meta, valor_meta)

    meta = mock_metas[-1]

    assert meta["nome"] == nome_meta
    assert meta["valor_meta"] == valor_meta
    assert meta["valor_atual"] == 0



@pytest.mark.parametrize(
    "id_meta, valor_adicionado, resultado_esperado",
    [
        (1, 120.0, True),
        (1, 100.0, True),
        (2, 0, True),
        (3, 50.0, False),
    ]
)
def test_adicionar_valor_meta(mock_carregar_metas, mock_metas, id_meta, valor_adicionado, resultado_esperado):

    sucesso_meta = adicionar_valor_meta(id_meta, valor_adicionado)
    assert sucesso_meta is resultado_esperado

@pytest.mark.parametrize(
    "id_meta, valor_adicionado, valor_esperado",
    [
        (1, 120.0, 720.0),
        (1, 100.0, 700.0),
        (2, 0, 0),
    ]
)
def test_adicionar_valor_meta_atualiza_valor(mock_carregar_metas, mock_metas, id_meta, valor_adicionado, valor_esperado):

    valor_anterior = 0

    for meta in mock_metas:
        if meta["id"] == id_meta:
            valor_anterior = meta["valor_atual"]

    adicionar_valor_meta(id_meta, valor_adicionado)

    for meta in mock_metas:
        if meta["id"] == id_meta:
            assert meta["valor_atual"] == valor_anterior + valor_adicionado


def test_adicionar_valor_meta_nao_ultrapassa_meta(
    mock_carregar_metas,
    mock_metas
):
    adicionar_valor_meta(3, 50.0)

    meta = mock_metas[2]

    assert meta["valor_atual"] == 100.0


@pytest.mark.parametrize(
    "novo_nome, valor_meta, valor_id, resultado_esperado",
    [
        ("pc novo", 3000.0, 1, True),
        ("carro novo", 150000.0, 2, True),
        ("meta inexistente", 500.0, 999, False),
    ]
)
def test_editar_meta(
    mock_carregar_metas,
    novo_nome,
    valor_meta,
    valor_id,
    resultado_esperado
):
    resultado = editar_meta(novo_nome, valor_meta, valor_id)

    assert resultado is resultado_esperado


def test_editar_meta_altera_dados(mock_carregar_metas, mock_metas):

    editar_meta("computador novo", 3000.0, 1)

    meta = mock_metas[0]

    assert meta["id"] == 1
    assert meta["nome"] == "computador novo"
    assert meta["valor_meta"] == 3000.0
    assert meta["valor_atual"] == 600.0


@pytest.mark.parametrize(
    "id_meta, resultado_esperado",
    [
        (1, True),
        (2, True),
        (999, False),
    ]
)
def test_remover_meta(mock_carregar_metas,mock_metas,id_meta, resultado_esperado):

    sucesso = remover_meta(id_meta)
    assert sucesso is resultado_esperado


def test_remover_meta_remove_id(mock_carregar_metas,mock_metas):
    remover_meta(1)

    assert all(
        meta["id"] != 1
        for meta in mock_metas
    )


@pytest.mark.parametrize(
    "id_meta",
    [
        1,
        2,
        999,
    ]
)
def test_buscar_meta_por_id(mock_carregar_metas,mock_metas,id_meta):

    resultado = buscar_meta_por_id(id_meta)

    if id_meta == 999:
        assert resultado is None
    else:
        meta_esperada = next(
            meta for meta in mock_metas
            if meta["id"] == id_meta
        )

        assert resultado == meta_esperada
