from pydantic import BaseModel


class UnidadeSchema(BaseModel):
    nome: str
    cidade: str
    endereco: str


class UnidadePublico(BaseModel):
    id: int
    nome: str
    cidade: str
    endereco: str
    aberta: bool

    model_config = {'from_attributes': True}
