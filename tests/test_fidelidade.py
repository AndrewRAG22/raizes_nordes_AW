from http import HTTPStatus


def test_ver_pontos(client, token):
    resposta = client.get(
        '/fidelidade/meus-pontos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert resposta.status_code == HTTPStatus.OK
    assert resposta.json()['pontos'] == 0


def test_ver_pontos_sem_fidelidade(client, token_gerente):
    resposta = client.get(
        '/fidelidade/meus-pontos',
        headers={'Authorization': f'Bearer {token_gerente}'},
    )
    assert resposta.status_code == HTTPStatus.NOT_FOUND


def test_resgatar_pontos_insuficientes(client, token):
    resposta = client.post(
        '/fidelidade/resgatar',
        headers={'Authorization': f'Bearer {token}'},
        json={'pontos': 10},
    )
    assert resposta.status_code == HTTPStatus.CONFLICT
