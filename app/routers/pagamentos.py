import json
import random
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.models import Pagamento, Pedido, Usuario
from app.infra.security import get_current_user
from app.schemas import PagamentoPublico, PagamentoSchema
from app.schemas.enums import StatusPagamento, StatusPedido

router = APIRouter(prefix='/pagamentos', tags=['pagamentos'])

DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def mock_gateway(forma_pagamento: str):
    nao_autorizado = 0.2
    aprovado = random.random() > nao_autorizado
    return {
        'gateway': 'mock_gateway',
        'forma_pagamento': forma_pagamento,
        'aprovado': aprovado,
        'codigo': 'TXN31415' if aprovado else None,
        'mensagem': 'Pagamento aprovado' if aprovado else 'Pagamento recusado',
    }


@router.post(
    '/', response_model=PagamentoPublico, status_code=HTTPStatus.CREATED
)
def solicitar_pagamento(
    dados: PagamentoSchema, session: DBSession, usuario: CurrentUser
):
    pedido = session.scalar(
        select(Pedido).where(
            Pedido.id == dados.pedido_id,
            Pedido.cliente_id == usuario.id,
        )
    )
    if not pedido:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Pedido não encontrado'
        )

    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Pedido cancelado ou processado',
        )

    processando = session.scalar(
        select(Pagamento).where(Pagamento.pedido_id == dados.pedido_id)
    )
    if processando:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Pedido já está sendo processado',
        )

    retorno = mock_gateway(dados.forma_pagamento)

    if retorno['aprovado']:
        status_pgto = StatusPagamento.APROVADO
        pedido.status = StatusPedido.EM_PREPARO
    else:
        status_pgto = StatusPagamento.RECUSADO
        pedido.status = StatusPedido.CANCELADO

    pagamento = Pagamento(
        pedido_id=dados.pedido_id,
        forma_pagamento=dados.forma_pagamento,
        status=status_pgto,
        payload_retorno=json.dumps(retorno),
    )
    session.add(pagamento)
    session.commit()
    session.refresh(pagamento)
    return pagamento
