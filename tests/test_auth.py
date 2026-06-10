from http import HTTPStatus


def test_registrar_usuario(client):
    response = client.post(
        '/auth/registrar',
        json={
            'username': 'Irinel',
            'nome': 'irinel Soares',
            'email': 'irinel@email.com',
            'senha': '12345',
            'consentimento_lgpd': True,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['email'] == 'irinel@email.com'
    assert response.json()['perfil'] == 'CLIENTE'


def test_registrar_usuario_duplicado(client):
    response = client.post(
        '/auth/registrar',
        json={
            'username': 'irinel',
            'nome': 'irinel Soares',
            'email': 'irinel@email.com',
            'senha': '12345',
            'consentimento_lgpd': True,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_login(client):
    client.post(
        '/auth/registrar',
        json={
            'username': 'Maxuel',
            'nome': 'Maxuel Araujo',
            'email': 'maxuel@email.com',
            'senha': '123456',
        },
    )
    response = client.post(
        '/auth/token',
        data={'username': 'maxuel@email.com', 'password': '123456'},
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()


def test_login_senha_errada(client):
    client.post(
        '/auth/registrar',
        json={
            'username': 'Max',
            'nome': 'Max Guedes',
            'email': 'max@email.com',
            'senha': '123457',
        },
    )
    response = client.post(
        '/auth/token',
        data={'username': 'max@email.com', 'password': 'nao-lembro'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
