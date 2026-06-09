from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.infra.models import PerfilUsuario, Usuario
from app.infra.security import get_current_user

User = Annotated[Usuario, Depends(get_current_user)]


def get_usuario_admin(usuario: User):
    perfil_do_usuario = usuario.perfil

    if perfil_do_usuario != PerfilUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Você não tem permissão de administrador.',
        )

    return usuario


def get_usuario_gerente(usuario: User):
    perfil = usuario.perfil

    eh_admin = perfil == PerfilUsuario.ADMIN
    eh_gerente = perfil == PerfilUsuario.GERENTE

    if not (eh_admin or eh_gerente):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Você precisa ser Gerente ou Admin para acessar aqui.',
        )

    return usuario
