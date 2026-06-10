from http import HTTPStatus


def test_get_me(client, token):
    response = client.get(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['email'] == 'Araujo@email.com'


def test_update_me(client, token):
    response = client.put(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'andrew95',
            'nome': 'Andrew Lançamento',
            'email': 'Araujoo@email.com',
            'senha': '123456',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['nome'] == 'Andrew Lançamento'


def test_delete_me(client, token):
    response = client.delete(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_get_me_sem_token(client):
    response = client.get('/users/me')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
