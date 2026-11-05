import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parent.parent
_env = dotenv_values(BACKEND_DIR / ".env")

if not _env.get("DATABASE_URL"):
    raise RuntimeError("Defina DATABASE_URL em .env na raiz do projeto")


TEST_DATABASE_URL = (
    os.getenv("TEST_DATABASE_URL")
    or _env.get("TEST_DATABASE_URL")
    or make_url(_env["DATABASE_URL"])
    .set(database="test_controle_financeiro")
    .render_as_string(hide_password=False)
)

_banco = make_url(TEST_DATABASE_URL).database or ""
if not _banco.startswith("test_"):
    raise RuntimeError(
        f"Os testes só podem rodar em um banco iniciado por 'test_' (recebido: {_banco!r})."
    )


os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.pop("TEST_DATABASE_URL", None)
os.environ["SECRET_KEY"] = "chave-secreta-apenas-para-testes"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from dados.database import Base, SessionLocal, engine  # noqa: E402
from dados.models import Usuario  # noqa: E402, F401
from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def banco_limpa():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client(banco_limpa):
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def db_session(banco_limpa):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def criar_usuario(client, db_session):
    def _criar(nome="user1", email="user1@example.com", senha="senha12345", ativo=True, admin=False):
        resposta = client.post(
            "/usuarios/",
            json={"nome": nome, "email": email, "senha": senha}
        )
        assert resposta.status_code == 201, resposta.text
        usuario = resposta.json()

        if not ativo or admin:
            registro = db_session.get(Usuario, usuario["id"])

            if not ativo:
                registro.ativo = False
                usuario["ativo"] = False

            if admin:
                registro.admin = True
                usuario["admin"] = True

            db_session.commit()
            db_session.expire_all()

        return usuario

    return _criar


@pytest.fixture
def autenticar(client):
    def _autenticar(email="user1@example.com", senha="senha12345"):
        resposta = client.post(
            "/auth/login",
            data={"username": email, "password": senha},
        )
        assert resposta.status_code == 200, resposta.text
        token = resposta.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _autenticar


@pytest.fixture
def usuario(criar_usuario):
    return criar_usuario()


@pytest.fixture
def headers(usuario, autenticar):
    return autenticar(email=usuario["email"])
