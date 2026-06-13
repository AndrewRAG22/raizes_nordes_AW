from pydantic import BaseModel, Field
from app.schemas.enums import CanalPedido, StatusPedido


class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int


class PedidoSchema(BaseModel):
    unidade_id: int
    canalPedido: CanalPedido
    itens: list[ItemPedidoSchema]


class ItemPedidoPublico(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: float

    model_config = {'from_attributes': True}


class PedidoPublico(BaseModel):
    id: int
    unidade_id: int
    cliente_id: int
    canalPedido: CanalPedido = Field(validation_alias='canal')
    status: StatusPedido
    total: float
    itens: list[ItemPedidoPublico]

    model_config = {
        'from_attributes': True,
        'populate_by_name': True,
    }


class AtualizarStatusSchema(BaseModel):
    status: StatusPedido