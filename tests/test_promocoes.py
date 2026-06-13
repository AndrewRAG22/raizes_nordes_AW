from http import HTTPStatus

from app.infra.models import Promocao


def test_listar_promocoes(client):
    resposta = client.get('/promocoes/')
    assert resposta.status_code == HTTPStatus.OK


def test_criar_promocao(client, token_gerente):
    resposta = client.post(
        '/promocoes/',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={'nome': 'Semana Consumidor', 'desconto': 35.0},
    )
    assert resposta.status_code == HTTPStatus.CREATED
    assert resposta.json()['nome'] == 'Semana Consumidor'


def test_criar_promocao_sem_permissao(client, token):
    resposta = client.post(
        '/promocoes/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Promoção Relâmpago', 'desconto': 80.0},
    )
    assert resposta.status_code == HTTPStatus.FORBIDDEN


def test_desativar_promocao(client, session, token_gerente):
    promocao = Promocao(nome='Promoção do Dia', desconto=10.0)
    session.add(promocao)
    session.commit()

    resposta = client.delete(
        f'/promocoes/{promocao.id}',
        headers={'Authorization': f'Bearer {token_gerente}'},
    )
    assert resposta.status_code == HTTPStatus.NO_CONTENT
