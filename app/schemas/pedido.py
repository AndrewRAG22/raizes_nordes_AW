from pydantic import BaseModel

from app.schemas.enums import CanalPedido, StatusPedido


class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int


class PedidoSchema(BaseModel):
    unidade_id: int
    canal: CanalPedido
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
    canal: CanalPedido
    status: StatusPedido
    total: float
    itens: list[ItemPedidoPublico]

    model_config = {'from_attributes': True}


class AtualizarStatusSchema(BaseModel):
    status: StatusPedido
