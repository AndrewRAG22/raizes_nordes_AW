from http import HTTPStatus


def test_main(client):
    response = client.get('/')

    assert response.json() == {'message': 'Teste, API funcionando!'}
    assert response.status_code == HTTPStatus.OK
