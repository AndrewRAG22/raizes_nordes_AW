from pydantic import BaseModel


class FidelidadePublico(BaseModel):
    id: int
    usuario_id: int
    pontos: int
    consentimento: bool

    model_config = {'from_attributes': True}


class ResgateSchema(BaseModel):
    pontos: int
