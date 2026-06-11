from http import HTTPStatus

from app.infra.models import Produto


def test_listar_produtos(client, session):
    produto = Produto(nome='Moqueca', preco=36.60)
    session.add(produto)
    session.commit()

    response = client.get('/produtos/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_buscar_produto(client, session):
    produto = Produto(nome='Sarapatel', preco=45.50)
    session.add(produto)
    session.commit()

    response = client.get(f'/produtos/{produto.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['nome'] == 'Sarapatel'


def test_buscar_produto_inexistente(client):
    response = client.get('/produtos/9999')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_criar_produto(client, token_gerente):
    response = client.post(
        '/produtos/',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={'nome': 'Cuscuz Nordestino', 'preco': 20.60},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'Cuscuz Nordestino'


def test_criar_produto_sem_permissao(client, token):
    response = client.post(
        '/produtos/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Bolo de Rolo', 'preco': 1.50},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_desativar_produto(client, session, token_gerente):
    produto = Produto(nome='Caranguejo', preco=24.00)
    session.add(produto)
    session.commit()

    response = client.delete(
        f'/produtos/{produto.id}',
        headers={'Authorization': f'Bearer {token_gerente}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
