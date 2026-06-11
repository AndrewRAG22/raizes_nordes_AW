from pydantic import BaseModel

from app.schemas.enums import StatusPagamento


class PagamentoSchema(BaseModel):
    pedido_id: int
    forma_pagamento: str


class PagamentoPublico(BaseModel):
    id: int
    pedido_id: int
    forma_pagamento: str
    status: StatusPagamento
    payload_retorno: str | None

    model_config = {'from_attributes': True}
