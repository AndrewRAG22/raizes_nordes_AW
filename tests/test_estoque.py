from http import HTTPStatus

from app.infra.models import Produto, Unidade


def test_consultar_estoque(client, session, token_gerente):
    unidade = Unidade(
        nome='Filial Shopping',
        cidade='Rio de Janeiro',
        endereco='Rua praia, 25',
    )
    session.add(unidade)
    session.commit()

    response = client.get(
        f'/unidades/{unidade.id}/estoque/',
        headers={'Authorization': f'Bearer {token_gerente}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_movimentar_entrada(client, session, token_gerente):
    unidade = Unidade(
        nome='Filial Shopping',
        cidade='Rio de Janeiro',
        endereco='Rua praia, 25',
    )
    quantidade_entrada = 10
    produto = Produto(nome='Sarapatel', preco=45.50)
    session.add_all([unidade, produto])
    session.commit()

    response = client.post(
        f'/unidades/{unidade.id}/estoque/movimentar',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={
            'produto_id': produto.id,
            'tipo': 'ENTRADA',
            'quantidade': quantidade_entrada,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['quantidade'] == quantidade_entrada


def test_movimentar_saida(client, session, token_gerente):
    unidade = Unidade(
        nome='Filial Shopping',
        cidade='Rio de Janeiro',
        endereco='Rua praia, 25',
    )
    quantidade_entrada = 5
    quantidade_saida = 3
    quantidade_final = quantidade_entrada - quantidade_saida
    produto = Produto(nome='Sarapatel', preco=45.50)
    session.add_all([unidade, produto])
    session.commit()

    client.post(
        f'/unidades/{unidade.id}/estoque/movimentar',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={
            'produto_id': produto.id,
            'tipo': 'ENTRADA',
            'quantidade': quantidade_entrada,
        },
    )

    response = client.post(
        f'/unidades/{unidade.id}/estoque/movimentar',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={
            'produto_id': produto.id,
            'tipo': 'SAIDA',
            'quantidade': quantidade_saida,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['quantidade'] == quantidade_final


def test_estoque_insuficiente(client, session, token_gerente):
    unidade = Unidade(
        nome='Filial Shopping',
        cidade='Rio de Janeiro',
        endereco='Rua praia, 25',
    )
    produto = Produto(nome='Sarapatel', preco=45.50)
    session.add_all([unidade, produto])
    session.commit()

    response = client.post(
        f'/unidades/{unidade.id}/estoque/movimentar',
        headers={'Authorization': f'Bearer {token_gerente}'},
        json={'produto_id': produto.id, 'tipo': 'SAIDA', 'quantidade': 50},
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_consultar_estoque_unidade_inexistente(client):
    response = client.get('/unidades/9999/estoque/')
    assert response.status_code == HTTPStatus.NOT_FOUND
