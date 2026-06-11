from pydantic import BaseModel

from app.schemas.enums import TipoMovimentacao


class MovimentacaoSchema(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int
    observacao: str | None = None


class EstoquePublico(BaseModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int

    model_config = {'from_attributes': True}


class MovimentacaoPublico(BaseModel):
    id: int
    estoque_id: int
    tipo: TipoMovimentacao
    quantidade: int
    observacao: str | None

    model_config = {'from_attributes': True}
