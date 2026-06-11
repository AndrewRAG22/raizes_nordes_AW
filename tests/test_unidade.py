from http import HTTPStatus

from app.infra.models import Unidade


def test_criar_unidade(client, token_gerente):
    response = client.post(
        '/unidades/',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={
            'nome': 'Filial Shopping',
            'cidade': 'Rio de Janeiro',
            'endereco': 'Rua praia, 25',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'Filial Shopping'


def test_criar_unidade_sem_permissao(client, token):
    response = client.post(
        '/unidades/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome': 'Filial Rua',
            'cidade': 'Rio de Janeiro',
            'endereco': 'Rua de baixo, 34',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_listar_unidades(client, session):
    unidade = Unidade(
        nome='Filial Galeria',
        cidade='Rio de Janeiro',
        endereco='Rua de cima, 14',
    )
    session.add(unidade)
    session.commit()

    response = client.get('/unidades/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_fechar_unidade(client, session, token_gerente):
    unidade = Unidade(
        nome='Loja Principal', cidade='Rio de Janeiro', endereco='Rua Araça, 5'
    )
    session.add(unidade)
    session.commit()

    response = client.delete(
        f'/unidades/{unidade.id}',
        headers={'Authorization': f'Bearer {token_gerente}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
