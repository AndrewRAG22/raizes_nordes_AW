from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.models import Fidelidade, Usuario
from app.infra.security import (
    criar_token_de_acesso,
    gerar_hash_da_senha,
    verificar_senha,
)
from app.schemas import TokenSchema, UsuarioPublico, UsuarioSchema

router = APIRouter(prefix='/auth', tags=['auth'])

DBSession = Annotated[Session, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    '/registrar',
    response_model=UsuarioPublico,
    status_code=HTTPStatus.CREATED,
)
def registrar(dados: UsuarioSchema, session: DBSession):
    usuario_existente = session.scalar(
        select(Usuario).where(
            (Usuario.email == dados.email)
            | (Usuario.username == dados.username)
        )
    )
    if usuario_existente:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email ou username já cadastrado',
        )

    novo_usuario = Usuario(
        username=dados.username,
        nome=dados.nome,
        email=dados.email,
        senha=gerar_hash_da_senha(dados.senha),
        consentimento_lgpd=dados.consentimento_lgpd,
    )
    session.add(novo_usuario)
    session.flush()

    if dados.consentimento_lgpd:
        fidelidade = Fidelidade(
            usuario_id=novo_usuario.id,
            consentimento=True,
        )
        session.add(fidelidade)
    session.commit()
    session.refresh(novo_usuario)

    return novo_usuario


@router.post('/token', response_model=TokenSchema)
def login(
    form_data: OAuth2Form,
    session: DBSession,
):
    usuario = session.scalar(
        select(Usuario).where(Usuario.email == form_data.username)
    )

    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou senha inválidos',
        )

    token = criar_token_de_acesso({'sub': usuario.email})
    return {'access_token': token, 'token_type': 'bearer'}
