import pytest

from dados.models import Categoria, Meta, Transacao, Usuario


@pytest.fixture
def outro_usuario(criar_usuario):
    return criar_usuario(nome="outro", email="outro@example.com", senha="senha12345")


@pytest.fixture
def admin(criar_usuario):
    return criar_usuario(
        nome="admin", email="admin@example.com", senha="senha12345", admin=True
    )


@pytest.fixture
def admin_headers(admin, autenticar):
    return autenticar(email=admin["email"])


def _requisitar(client, metodo, caminho, headers=None, json=None):
    return client.request(metodo.upper(), caminho, headers=headers, json=json)


def test_criar_usuario(client):
    resposta = client.post(
        "/usuarios/",
        json={"nome": "ana", "email": "ana@example.com", "senha": "senha12345"},
    )

    assert resposta.status_code == 201, resposta.text

    corpo = resposta.json()
    assert corpo["nome"] == "ana"
    assert corpo["email"] == "ana@example.com"
    assert corpo["ativo"] is True
    assert corpo["admin"] is False
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_criar_usuario_ignora_campos_privilegiados(client):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "ana",
            "email": "ana@example.com",
            "senha": "senha12345",
            "admin": True,
            "ativo": False,
        },
    )

    assert resposta.status_code == 201, resposta.text

    corpo = resposta.json()
    assert corpo["admin"] is False
    assert corpo["ativo"] is True


def test_listar_usuarios_comum_retorna_apenas_a_si(client, usuario, outro_usuario, headers):
    resposta = client.get("/usuarios/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert [item["id"] for item in resposta.json()] == [usuario["id"]]


def test_listar_usuarios_admin_retorna_todos(
    client, usuario, outro_usuario, admin, admin_headers
):
    resposta = client.get("/usuarios/", headers=admin_headers)

    assert resposta.status_code == 200, resposta.text
    assert {item["email"] for item in resposta.json()} == {
        usuario["email"],
        outro_usuario["email"],
        admin["email"],
    }


def test_buscar_usuario_proprio(client, usuario, headers):
    resposta = client.get(f"/usuarios/{usuario['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["email"] == usuario["email"]


def test_buscar_outro_usuario_como_admin(client, outro_usuario, admin_headers):
    resposta = client.get(f"/usuarios/{outro_usuario['id']}", headers=admin_headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["id"] == outro_usuario["id"]


def test_editar_usuario_proprio(client, usuario, headers):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"nome": "nome atualizado"},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "nome atualizado"
    assert resposta.json()["email"] == usuario["email"]


def test_editar_email_proprio_permite_login_com_novo_email(
    client, usuario, headers, autenticar
):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"email": "novo@example.com"},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["email"] == "novo@example.com"

    autenticar(email="novo@example.com", senha="senha12345")

    login_antigo = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senha12345"},
    )
    assert login_antigo.status_code == 401, login_antigo.text


def test_editar_usuario_mantendo_o_proprio_email(client, usuario, headers):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"email": usuario["email"]},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["email"] == usuario["email"]


def test_editar_senha_propria_e_login(client, usuario, headers, autenticar):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"senha": "novasenha123"},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text

    autenticar(email=usuario["email"], senha="novasenha123")

    login_antigo = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senha12345"},
    )
    assert login_antigo.status_code == 401, login_antigo.text


def test_editar_outro_usuario_como_admin(client, outro_usuario, admin_headers):
    resposta = client.put(
        f"/usuarios/{outro_usuario['id']}",
        json={"nome": "editado pelo admin"},
        headers=admin_headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "editado pelo admin"


def test_admin_altera_ativo_de_outro_usuario(
    client, outro_usuario, admin_headers
):
    resposta = client.put(
        f"/usuarios/{outro_usuario['id']}",
        json={"ativo": False},
        headers=admin_headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["ativo"] is False

    login = client.post(
        "/auth/login",
        data={"username": outro_usuario["email"], "password": "senha12345"},
    )
    assert login.status_code == 401, login.text


def test_admin_nao_pode_ser_alterado_pela_api(client, usuario, headers):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"admin": True},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["admin"] is False


def test_cancelar_propria_conta(client, usuario, headers):
    resposta = client.patch(f"/usuarios/{usuario['id']}/cancelar", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["ativo"] is False

    login = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senha12345"},
    )
    assert login.status_code == 401, login.text


def test_cancelar_outro_usuario_como_admin(client, outro_usuario, admin_headers):
    resposta = client.patch(
        f"/usuarios/{outro_usuario['id']}/cancelar", headers=admin_headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["ativo"] is False


def test_remover_propria_conta(client, usuario, headers, db_session):
    resposta = client.delete(f"/usuarios/{usuario['id']}", headers=headers)

    assert resposta.status_code == 204, resposta.text
    assert resposta.text == ""
    assert db_session.get(Usuario, usuario["id"]) is None


def test_remover_outro_usuario_como_admin(client, outro_usuario, admin_headers, db_session):
    resposta = client.delete(f"/usuarios/{outro_usuario['id']}", headers=admin_headers)

    assert resposta.status_code == 204, resposta.text
    assert db_session.get(Usuario, outro_usuario["id"]) is None


def test_remover_usuario_apaga_dados_associados(client, usuario, headers, db_session):
    categoria = client.post(
        "/categorias/",
        json={"nome": "Moradia", "valor_inicial": 0, "valor_limite": 1000},
        headers=headers,
    )
    assert categoria.status_code == 201, categoria.text

    transacao = client.post(
        "/transacoes/",
        json={
            "descricao": "Aluguel",
            "valor": 100,
            "tipo": "despesa",
            "data": "2026-01-05",
            "categoria_id": categoria.json()["id"],
        },
        headers=headers,
    )
    assert transacao.status_code == 201, transacao.text

    meta = client.post(
        "/metas/",
        json={"nome": "Reserva", "valor_inicial": 0, "valor_final": 1000},
        headers=headers,
    )
    assert meta.status_code == 201, meta.text

    resposta = client.delete(f"/usuarios/{usuario['id']}", headers=headers)
    assert resposta.status_code == 204, resposta.text

    db_session.expire_all()
    assert db_session.query(Categoria).filter(Categoria.id == categoria.json()["id"]).count() == 0
    assert db_session.query(Transacao).filter(Transacao.id == transacao.json()["id"]).count() == 0
    assert db_session.query(Meta).filter(Meta.id == meta.json()["id"]).count() == 0


def test_criar_usuario_email_duplicado(client, criar_usuario):
    criar_usuario(email="duplicado@example.com")

    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "outro nome",
            "email": "duplicado@example.com",
            "senha": "senha12345",
        },
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Email já cadastrado"


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": "ab", "email": "ana@example.com", "senha": "senha12345"},
        {"nome": "a" * 101, "email": "ana@example.com", "senha": "senha12345"},
        {"nome": "ana", "email": "email-invalido", "senha": "senha12345"},
        {"nome": "ana", "email": "ana@example.com", "senha": "12345"},
        {"nome": "ana", "email": "ana@example.com", "senha": "      "},
        {},
    ],
)
def test_criar_usuario_dados_invalidos(client, dados):
    resposta = client.post("/usuarios/", json=dados)

    assert resposta.status_code == 422, resposta.text


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/usuarios/"),
        ("get", "/usuarios/1"),
        ("put", "/usuarios/1"),
        ("patch", "/usuarios/1/cancelar"),
        ("delete", "/usuarios/1"),
    ],
)
def test_rotas_protegidas_sem_token(client, metodo, caminho):
    json = {"nome": "teste"} if metodo == "put" else None

    resposta = _requisitar(client, metodo, caminho, json=json)

    assert resposta.status_code == 401, resposta.text


def test_listar_usuarios_token_invalido(client):
    resposta = client.get(
        "/usuarios/", headers={"Authorization": "Bearer token.invalido.aqui"}
    )

    assert resposta.status_code == 401, resposta.text


def test_buscar_outro_usuario_sem_permissao(client, outro_usuario, headers):
    resposta = client.get(f"/usuarios/{outro_usuario['id']}", headers=headers)

    assert resposta.status_code == 403, resposta.text
    assert resposta.json()["detail"] == "Sem permissão"


@pytest.mark.parametrize(
    ("metodo", "caminho", "status_esperado"),
    [
        ("get", "/usuarios/999999", 403),
        ("put", "/usuarios/999999", 404),
        ("patch", "/usuarios/999999/cancelar", 404),
        ("delete", "/usuarios/999999", 404),
    ],
)
def test_operacoes_em_usuario_inexistente_como_comum(
    client, headers, metodo, caminho, status_esperado
):
    json = {"nome": "teste"} if metodo == "put" else None

    resposta = _requisitar(client, metodo, caminho, headers=headers, json=json)

    assert resposta.status_code == status_esperado, resposta.text


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/usuarios/999999"),
        ("put", "/usuarios/999999"),
        ("patch", "/usuarios/999999/cancelar"),
        ("delete", "/usuarios/999999"),
    ],
)
def test_operacoes_em_usuario_inexistente_como_admin(
    client, admin_headers, metodo, caminho
):
    json = {"nome": "teste"} if metodo == "put" else None

    resposta = _requisitar(client, metodo, caminho, headers=admin_headers, json=json)

    assert resposta.status_code == 404, resposta.text


def test_editar_outro_usuario_sem_permissao(client, outro_usuario, headers):
    resposta = client.put(
        f"/usuarios/{outro_usuario['id']}",
        json={"nome": "invasao"},
        headers=headers,
    )

    assert resposta.status_code == 403, resposta.text


def test_editar_usuario_sem_permissao_nao_altera_dados(client, usuario, headers):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"nome": "nao deve salvar", "ativo": False},
        headers=headers,
    )

    assert resposta.status_code == 403, resposta.text
    assert resposta.json()["detail"] == "Apenas administradores"

    perfil = client.get("/auth/me", headers=headers)
    assert perfil.status_code == 200, perfil.text
    assert perfil.json()["nome"] == usuario["nome"]


def test_editar_usuario_email_duplicado(client, usuario, outro_usuario, headers):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json={"email": outro_usuario["email"]},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Email já cadastrado"


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": "ab"},
        {"nome": "a" * 101},
        {"email": "email-invalido"},
        {"senha": "12345"},
    ],
)
def test_editar_usuario_dados_invalidos(client, usuario, headers, dados):
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 422, resposta.text


def test_cancelar_outro_usuario_sem_permissao(client, outro_usuario, headers):
    resposta = client.patch(
        f"/usuarios/{outro_usuario['id']}/cancelar", headers=headers
    )

    assert resposta.status_code == 403, resposta.text


def test_remover_outro_usuario_sem_permissao(client, outro_usuario, headers):
    resposta = client.delete(f"/usuarios/{outro_usuario['id']}", headers=headers)

    assert resposta.status_code == 403, resposta.text
