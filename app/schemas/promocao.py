from pydantic import BaseModel


class PromocaoSchema(BaseModel):
    nome: str
    desconto: float


class PromocaoPublico(BaseModel):
    id: int
    nome: str
    desconto: float
    ativa: bool

    model_config = {'from_attributes': True}
