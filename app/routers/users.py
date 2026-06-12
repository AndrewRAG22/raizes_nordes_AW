from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.models import Fidelidade, Usuario
from app.infra.security import gerar_hash_da_senha, get_current_user
from app.schemas import UsuarioPublico, UsuarioSchema

router = APIRouter(prefix='/users', tags=['users'])

DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.get('/me', response_model=UsuarioPublico)
def get_me(usuario: CurrentUser):
    return usuario


@router.put('/me', response_model=UsuarioPublico)
def update_me(dados: UsuarioSchema, usuario: CurrentUser, session: DBSession):
    conflito = session.scalar(
        select(Usuario).where(
            (Usuario.email == dados.email)
            | (Usuario.username == dados.username)
        )
    )
    if conflito:
        if conflito.username == dados.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='O username digitado já esta em uso',
            )
        elif conflito.email == dados.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='O email digitado já esta em uso',
            )

    usuario.nome = dados.nome
    usuario.email = dados.email
    usuario.username = dados.username
    usuario.senha = gerar_hash_da_senha(dados.senha)

    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete('/me', status_code=HTTPStatus.NO_CONTENT)
def delete_me(usuario: CurrentUser, session: DBSession):
    fidelidade = session.scalar(
        select(Fidelidade).where(Fidelidade.usuario_id == usuario.id)
    )
    if fidelidade:
        session.delete(fidelidade)

    session.delete(usuario)
    session.commit()
