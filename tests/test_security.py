from http import HTTPStatus

from app.infra.security import (
    criar_token_de_acesso,
    decodificar_token,
    gerar_hash_da_senha,
)


def test_hash_senha():
    hash = gerar_hash_da_senha('minhasenha123')
    assert hash != 'minhasenha123'


def test_token():
    dados = {'sub': 'andrew@email.com'}
    token = criar_token_de_acesso(dados)
    assert decodificar_token(token)['sub'] == 'andrew@email.com'


def test_acesso_negado_sem_token(client):
    response = client.delete('/users/me')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['error'] == 'NAO_AUTENTICADO'


def test_acesso_com_token_invalido(client):
    response = client.delete(
        '/users/me', headers={'Authorization': 'Bearer token-falso'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
