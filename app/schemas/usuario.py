from pydantic import BaseModel, EmailStr

from app.schemas.enums import PerfilUsuario


class UsuarioSchema(BaseModel):
    username: str
    nome: str
    email: EmailStr
    senha: str
    consentimento_lgpd: bool = False


class UsuarioPublico(BaseModel):
    id: int
    username: str
    nome: str
    email: EmailStr
    perfil: PerfilUsuario

    model_config = {'from_attributes': True}


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
