from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.depends import get_usuario_gerente
from app.infra.database import get_session
from app.infra.models import Estoque, MovimentacaoEstoque, Produto, Unidade
from app.schemas import EstoquePublico, MovimentacaoSchema

router = APIRouter(prefix='/unidades/{unidade_id}/estoque', tags=['estoque'])

DBSession = Annotated[Session, Depends(get_session)]


@router.get('/', response_model=list[EstoquePublico])
def consultar_estoque(unidade_id: int, session: DBSession):
    unidade = session.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    return session.scalars(
        select(Estoque).where(Estoque.unidade_id == unidade_id)
    ).all()


@router.post(
    '/movimentar',
    response_model=EstoquePublico,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_usuario_gerente)],
)
def movimentar_estoque(
    unidade_id: int, dados: MovimentacaoSchema, session: DBSession
):
    unidade = session.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    produto = session.scalar(
        select(Produto).where(Produto.id == dados.produto_id)
    )
    if not produto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado',
        )

    estoque = session.scalar(
        select(Estoque).where(
            Estoque.unidade_id == unidade_id,
            Estoque.produto_id == dados.produto_id,
        )
    )
    if not estoque:
        estoque = Estoque(
            unidade_id=unidade_id,
            produto_id=dados.produto_id,
        )
        session.add(estoque)
        session.flush()

    if dados.tipo.value == 'SAIDA':
        if estoque.quantidade < dados.quantidade:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f'Estoque insuficiente.Disponível:{estoque.quantidade}',
            )
        estoque.quantidade -= dados.quantidade
    else:
        estoque.quantidade += dados.quantidade

    movimentacao = MovimentacaoEstoque(
        estoque_id=estoque.id,
        tipo=dados.tipo,
        quantidade=dados.quantidade,
        observacao=dados.observacao,
    )
    session.add(movimentacao)
    session.commit()
    session.refresh(estoque)
    return estoque
