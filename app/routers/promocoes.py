from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.depends import get_usuario_gerente
from app.infra.database import get_session
from app.infra.models import Promocao
from app.schemas import PromocaoPublico, PromocaoSchema

router = APIRouter(prefix='/promocoes', tags=['promocoes'])

DBSession = Annotated[Session, Depends(get_session)]


@router.get('/', response_model=list[PromocaoPublico])
def listar_promocoes(session: DBSession, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    return session.scalars(
        select(Promocao).where(Promocao.ativa.is_(True))
        .offset(offset).limit(limit)
    ).all()


@router.post(
    '/',
    response_model=PromocaoPublico,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_usuario_gerente)],
)
def criar_promocao(dados: PromocaoSchema, session: DBSession):
    promocao = Promocao(nome=dados.nome, desconto=dados.desconto)
    session.add(promocao)
    session.commit()
    session.refresh(promocao)
    return promocao


@router.delete(
    '/{promocao_id}',
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(get_usuario_gerente)],
)
def desativar_promocao(promocao_id: int, session: DBSession):
    promocao = session.scalar(
        select(Promocao).where(Promocao.id == promocao_id)
    )
    if not promocao:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Promoção não foi encontrada',
        )
    promocao.ativa = False
    session.commit()
