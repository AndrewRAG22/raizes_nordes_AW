from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.depends import get_usuario_gerente
from app.infra.database import get_session
from app.infra.models import Unidade
from app.schemas import UnidadePublico, UnidadeSchema

router = APIRouter(prefix='/unidades', tags=['unidades'])

DBSession = Annotated[Session, Depends(get_session)]


@router.get('/', response_model=list[UnidadePublico])
def listar_unidades(session: DBSession):
    return session.scalars(
        select(Unidade).where(Unidade.aberta.is_(True))
    ).all()


@router.post(
    '/',
    response_model=UnidadePublico,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_usuario_gerente)],
)
def criar_unidade(dados: UnidadeSchema, session: DBSession):
    unidade = Unidade(
        nome=dados.nome,
        cidade=dados.cidade,
        endereco=dados.endereco,
    )
    session.add(unidade)
    session.commit()
    session.refresh(unidade)
    return unidade


@router.patch(
    '/{unidade_id}',
    response_model=UnidadePublico,
    dependencies=[Depends(get_usuario_gerente)],
)
def atualizar_unidade(
    unidade_id: int, dados: UnidadeSchema, session: DBSession
):
    unidade = session.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não foi encontrada',
        )

    unidade.nome = dados.nome
    unidade.cidade = dados.cidade
    unidade.endereco = dados.endereco

    session.commit()
    session.refresh(unidade)
    return unidade


@router.delete(
    '/{unidade_id}',
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(get_usuario_gerente)],
)
def fechar_unidade(unidade_id: int, session: DBSession):
    unidade = session.scalar(select(Unidade).where(Unidade.id == unidade_id))
    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não foi encontrada',
        )

    unidade.aberta = False
    session.commit()
