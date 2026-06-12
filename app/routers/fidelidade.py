from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.models import Fidelidade, Usuario
from app.infra.security import get_current_user
from app.schemas import FidelidadePublico, ResgateSchema

router = APIRouter(prefix='/fidelidade', tags=['fidelidade'])

DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]

PONTOS_POR_REAL = 1


@router.get('/meus-pontos', response_model=FidelidadePublico)
def ver_pontos(usuario: CurrentUser, session: DBSession):
    fidelidade = session.scalar(
        select(Fidelidade).where(Fidelidade.usuario_id == usuario.id)
    )
    if not fidelidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Você não aderiu ao programa de fidelidade',
        )
    return fidelidade


@router.post('/resgatar', response_model=FidelidadePublico)
def resgatar_pontos(
    dados: ResgateSchema, usuario: CurrentUser, session: DBSession
):
    fidelidade = session.scalar(
        select(Fidelidade).where(Fidelidade.usuario_id == usuario.id)
    )
    if not fidelidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Você não aderiu ao programa de fidelidade',
        )

    if not fidelidade.consentimento:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você precisa aceitar os termos para usar o programa',
        )

    if dados.pontos <= 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Quantidade de pontos insuficiente',
        )

    if fidelidade.pontos < dados.pontos:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'Pontos insuficientes. Você tem {fidelidade.pontos}pontos',
        )

    fidelidade.pontos -= dados.pontos
    session.commit()
    session.refresh(fidelidade)
    return fidelidade
