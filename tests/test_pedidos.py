from http import HTTPStatus

from app.infra.models import Estoque, Produto, Unidade


def criar_contexto(session):
    unidade = Unidade(
        nome='Filial Rua', cidade='Rio de Janeiro', endereco='Rua de baixo, 34'
    )
    produto = Produto(nome='Moqueca', preco=36.60)
    session.add_all([unidade, produto])
    session.flush()

    estoque = Estoque(
        unidade_id=unidade.id, produto_id=produto.id, quantidade=5
    )
    session.add(estoque)
    session.commit()
    return unidade, produto


def test_criar_pedido(client, session, token):
    unidade, produto = criar_contexto(session)

    response = client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'APP',
            'itens': [{'produto_id': produto.id, 'quantidade': 1}],
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['total'] == float(produto.preco)
    assert response.json()['canalPedido'] == 'APP'


def test_criar_pedido_estoque_insuficiente(client, session, token):
    unidade, produto = criar_contexto(session)

    response = client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'TOTEM',
            'itens': [{'produto_id': produto.id, 'quantidade': 20}],
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_criar_pedido_produto_inexistente(client, session, token):
    unidade = Unidade(
        nome='Filial Rua', cidade='Rio de Janeiro', endereco='Rua de baixo, 34'
    )
    session.add(unidade)
    session.commit()

    response = client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'WEB',
            'itens': [{'produto_id': 9999, 'quantidade': 10}],
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_listar_pedidos(client, session, token):
    unidade, produto = criar_contexto(session)

    client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'APP',
            'itens': [{'produto_id': produto.id, 'quantidade': 1}],
        },
    )

    response = client.get(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1


def test_cancelar_pedido(client, session, token):
    unidade, produto = criar_contexto(session)

    pedido = client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'APP',
            'itens': [{'produto_id': produto.id, 'quantidade': 1}],
        },
    ).json()

    response = client.delete(
        f'/pedidos/{pedido["id"]}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
