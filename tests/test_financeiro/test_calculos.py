from unittest.mock import patch

import pytest

from financeiro.transacoes.calculos import (
    total_despesas,
    total_receitas,
    saldo_atual,
    obter_resumo,
    calcular_gasto_categoria,
)


@pytest.fixture
def carregar_transacoes_mock(mock_transacoes):
    with patch(
        "financeiro.transacoes.calculos.carregar_json",
        return_value=mock_transacoes,
    ):
        yield


def test_total_despesas(carregar_transacoes_mock):
    total = total_despesas()

    assert total == 15


def test_total_receitas(carregar_transacoes_mock):
    total = total_receitas()

    assert total == 1050


def test_saldo_atual(carregar_transacoes_mock):
    saldo = saldo_atual()

    assert saldo == 1035


def test_obter_resumo(carregar_transacoes_mock):
    resumo = obter_resumo()

    assert resumo["saldo"] == 1035
    assert resumo["receitas"] == 1050
    assert resumo["despesas"] == 15


@pytest.mark.parametrize(
    "id_categoria, esperado",
    [
        (1, 5),
        (2, 10),
        (999, 0),
    ],
)
def test_calcular_gasto_categoria(
    carregar_transacoes_mock,
    id_categoria,
    esperado,
):
    total = calcular_gasto_categoria(id_categoria)

    assert total == esperado