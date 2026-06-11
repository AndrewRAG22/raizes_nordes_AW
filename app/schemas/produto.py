from pydantic import BaseModel


class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    disponivel: bool = True


class ProdutoPublico(BaseModel):
    id: int
    nome: str
    preco: float
    disponivel: bool

    model_config = {'from_attributes': True}
