from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.models import Usuario
from app.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def gerar_hash_da_senha(senha: str):
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash: str):
    return pwd_context.verify(senha, hash)


def criar_token_de_acesso(dados: dict):
    para_codificar = dados.copy()
    expiracao = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    para_codificar.update({'exp': expiracao})

    codificar_jwt = encode(
        para_codificar, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return codificar_jwt


def decodificar_token(token: str):
    decodificar_jwt = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    return decodificar_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token inválido ou expirado',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decodificar_token(token)
        email = payload.get('sub')
        if not email:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    usuario = session.scalar(select(Usuario).where(Usuario.email == email))

    if not usuario:
        raise credentials_exception

    return usuario
