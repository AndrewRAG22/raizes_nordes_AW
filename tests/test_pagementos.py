from http import HTTPStatus
from unittest.mock import patch

from app.infra.models import Estoque, Produto, Unidade


def criar_pedido(client, session, token):
    unidade = Unidade(
        nome='Filial Galeria',
        cidade='Rio de Janeiro',
        endereco='Rua de cima, 14',
    )
    produto = Produto(nome='Muqueca', preco=30.25)
    session.add_all([unidade, produto])
    session.flush()
    estoque = Estoque(
        unidade_id=unidade.id, produto_id=produto.id, quantidade=10
    )
    session.add(estoque)
    session.commit()

    resposta = client.post(
        '/pedidos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'unidade_id': unidade.id,
            'canalPedido': 'APP',
            'itens': [{'produto_id': produto.id, 'quantidade': 1}],
        },
    )
    return resposta.json()


def test_pagamento_aprovado(client, session, token):
    pedido = criar_pedido(client, session, token)

    with patch('app.routers.pagamentos.mock_gateway') as mock:
        mock.return_value = {
            'gateway': 'mock_gateway',
            'forma_pagamento': 'PIX',
            'aprovado': True,
            'codigo': 'TXN314',
            'mensagem': 'Pagamento aprovado',
        }

        resposta = client.post(
            '/pagamentos/',
            headers={'Authorization': f'Bearer {token}'},
            json={'pedido_id': pedido['id'], 'forma_pagamento': 'PIX'},
        )

    assert resposta.status_code == HTTPStatus.CREATED
    assert resposta.json()['status'] == 'APROVADO'


def test_pagamento_recusado(client, session, token):
    pedido = criar_pedido(client, session, token)

    with patch('app.routers.pagamentos.mock_gateway') as mock:
        mock.return_value = {
            'gateway': 'mock_gateway',
            'forma_pagamento': 'CARTAO CREDITO',
            'aprovado': False,
            'codigo': None,
            'mensagem': 'Pagamento recusado',
        }

        resposta = client.post(
            '/pagamentos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'pedido_id': pedido['id'],
                'forma_pagamento': 'CARTAO CREDITO',
            },
        )

    assert resposta.status_code == HTTPStatus.CREATED
    assert resposta.json()['status'] == 'RECUSADO'


def test_processamento_pedido(client, session, token):
    pedido = criar_pedido(client, session, token)

    with patch('app.routers.pagamentos.mock_gateway') as mock:
        mock.return_value = {
            'gateway': 'mock_gateway',
            'forma_pagamento': 'CARTAO DEBITO',
            'aprovado': True,
            'codigo': 'TXN42',
            'mensagem': 'Pagamento aprovado',
        }

        client.post(
            '/pagamentos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'pedido_id': pedido['id'],
                'forma_pagamento': 'CARTAO DEBITO',
            },
        )

    resposta = client.get(
        f'/pedidos/{pedido["id"]}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert resposta.json()['status'] == 'EM_PREPARO'


def test_pagamento_duplicado(client, session, token):
    pedido = criar_pedido(client, session, token)

    with patch('app.routers.pagamentos.mock_gateway') as mock:
        mock.return_value = {
            'gateway': 'mock_gateway',
            'forma_pagamento': 'CARTAO CREDITO',
            'aprovado': True,
            'codigo': 'TXN123',
            'mensagem': 'Pagamento aprovado',
        }

        client.post(
            '/pagamentos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'pedido_id': pedido['id'],
                'forma_pagamento': 'CARTAO CREDITO',
            },
        )

        resposta = client.post(
            '/pagamentos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'pedido_id': pedido['id'],
                'forma_pagamento': 'CARTAO CREDITO',
            },
        )

    assert resposta.status_code == HTTPStatus.CONFLICT
