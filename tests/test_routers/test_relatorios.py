import pytest


def criar_transacao(client, headers, **dados):
    payload = {
        "descricao": "Compra",
        "valor": 50,
        "tipo": "despesa",
        "data": "2026-10-01",
    }
    payload.update(dados)
    return client.post("/transacoes/", json=payload, headers=headers)


def test_valor_receita_soma_apenas_receitas_do_mes(client, headers):
    for valor, data in (
        (1000, "2026-10-01"),
        (500.5, "2026-10-31"),
        (300, "2026-11-01"),
    ):
        assert criar_transacao(
            client, headers, valor=valor, tipo="receita", data=data
        ).status_code == 201

    assert criar_transacao(
        client, headers, valor=999, tipo="despesa", data="2026-10-15"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_receita?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 1500.5}


def test_valor_receita_mes_sem_receitas_retorna_zero(client, headers):
    resposta = client.get(
        "/relatorios/valor_receita?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 0.0}


def test_valor_receita_nao_soma_de_outro_usuario(
    client, headers, outro_headers
):
    assert criar_transacao(
        client, headers, valor=100, tipo="receita", data="2026-10-05"
    ).status_code == 201
    assert criar_transacao(
        client, outro_headers, valor=500, tipo="receita", data="2026-10-05"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_receita?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 100.0}


def test_valor_receita_dezembro_nao_inclui_janeiro(client, headers):
    assert criar_transacao(
        client, headers, valor=200, tipo="receita", data="2026-12-31"
    ).status_code == 201
    assert criar_transacao(
        client, headers, valor=700, tipo="receita", data="2027-01-01"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_receita?ano=2026&mes=12", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 200.0}


@pytest.mark.parametrize(
    "query",
    [
        "ano=1999&mes=10",
        "ano=2101&mes=10",
        "ano=2026&mes=0",
        "ano=2026&mes=13",
        "ano=2026",
        "mes=10",
    ],
)
def test_valor_receita_parametros_invalidos(client, headers, query):
    resposta = client.get(f"/relatorios/valor_receita?{query}", headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_valor_receita_token_invalido(client):
    resposta = client.get(
        "/relatorios/valor_receita?ano=2026&mes=10",
        headers={"Authorization": "Bearer token.invalido.aqui"},
    )

    assert resposta.status_code == 401, resposta.text


@pytest.mark.parametrize(
    "endpoint,tipo",
    [
        ("/relatorios/receitas", "receita"),
        ("/relatorios/despesas", "despesa"),
    ],
)
def test_relatorios_lista_apenas_tipo_correto(client, headers, endpoint, tipo):
    outro = "despesa" if tipo == "receita" else "receita"

    assert criar_transacao(
        client, headers, descricao="Certa", valor=100, tipo=tipo, data="2026-10-01"
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Outra", valor=50, tipo=outro, data="2026-10-02"
    ).status_code == 201

    resposta = client.get(endpoint, headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["total"] == 1
    assert [t["descricao"] for t in resposta.json()["items"]] == ["Certa"]


@pytest.mark.parametrize(
    "endpoint,tipo",
    [
        ("/relatorios/receitas", "receita"),
        ("/relatorios/despesas", "despesa"),
    ],
)
def test_relatorios_lista_busca(client, headers, endpoint, tipo):
    assert criar_transacao(
        client, headers, descricao="Mercado", valor=100, tipo=tipo, data="2026-10-01"
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Farmácia", valor=50, tipo=tipo, data="2026-10-02"
    ).status_code == 201

    resposta = client.get(endpoint, params={"busca": "merc"}, headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["total"] == 1
    assert [t["descricao"] for t in resposta.json()["items"]] == ["Mercado"]


def test_valor_despesas_soma_apenas_despesas_do_mes(client, headers):
    for valor, data in (
        (200, "2026-10-01"),
        (300.5, "2026-10-31"),
        (900, "2026-11-01"),
    ):
        assert criar_transacao(
            client, headers, valor=valor, tipo="despesa", data=data
        ).status_code == 201

    assert criar_transacao(
        client, headers, valor=999, tipo="receita", data="2026-10-15"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_despesas?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 500.5}


def test_valor_despesas_mes_sem_despesas_retorna_zero(client, headers):
    resposta = client.get(
        "/relatorios/valor_despesas?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 0.0}


def test_valor_despesas_nao_soma_de_outro_usuario(
    client, headers, outro_headers
):
    assert criar_transacao(
        client, headers, valor=100, tipo="despesa", data="2026-10-05"
    ).status_code == 201
    assert criar_transacao(
        client, outro_headers, valor=500, tipo="despesa", data="2026-10-05"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_despesas?ano=2026&mes=10", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 100.0}


def test_valor_despesas_dezembro_nao_inclui_janeiro(client, headers):
    assert criar_transacao(
        client, headers, valor=200, tipo="despesa", data="2026-12-31"
    ).status_code == 201
    assert criar_transacao(
        client, headers, valor=700, tipo="despesa", data="2027-01-01"
    ).status_code == 201

    resposta = client.get(
        "/relatorios/valor_despesas?ano=2026&mes=12", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {"valor_total": 200.0}


@pytest.mark.parametrize(
    "query",
    [
        "ano=1999&mes=10",
        "ano=2101&mes=10",
        "ano=2026&mes=0",
        "ano=2026&mes=13",
        "ano=2026",
        "mes=10",
    ],
)
def test_valor_despesas_parametros_invalidos(client, headers, query):
    resposta = client.get(f"/relatorios/valor_despesas?{query}", headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_valor_despesas_token_invalido(client):
    resposta = client.get(
        "/relatorios/valor_despesas?ano=2026&mes=10",
        headers={"Authorization": "Bearer token.invalido.aqui"},
    )

    assert resposta.status_code == 401, resposta.text

