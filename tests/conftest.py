import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infra.database import get_session
from app.infra.models import PerfilUsuario, Usuario, table_registry
from app.infra.security import criar_token_de_acesso, gerar_hash_da_senha
from app.main import app


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.close()

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def usuario(session):
    usuario = Usuario(
        username='andrew94',
        nome='Andrew Lançamento',
        email='Araujo@email.com',
        senha=gerar_hash_da_senha('123456'),
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture
def token(usuario):
    return criar_token_de_acesso({'sub': usuario.email})


@pytest.fixture
def usuario_gerente(session):
    usuario = Usuario(
        username='gerente',
        nome='Cristina Nascimento',
        email='Cris_Gerente@email.com',
        senha=gerar_hash_da_senha('123456'),
        perfil=PerfilUsuario.GERENTE,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@pytest.fixture
def token_gerente(usuario_gerente):
    return criar_token_de_acesso({'sub': usuario_gerente.email})
