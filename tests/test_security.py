from app.infra.security import (
    criar_token_de_acesso,
    decodificar_token,
    gerar_hash_da_senha,
)


def test_hash_senha():
    hash = gerar_hash_da_senha('minhasenha123')
    assert hash != 'minhasenha123'


def test_token_logica():
    dados = {'sub': 'andrew@email.com'}
    token = criar_token_de_acesso(dados)
    assert decodificar_token(token)['sub'] == 'andrew@email.com'
