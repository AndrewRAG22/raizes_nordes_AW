from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.depends import get_usuario_gerente
from app.infra.database import get_session
from app.infra.models import Produto
from app.schemas import ProdutoPublico, ProdutoSchema

router = APIRouter(prefix='/produtos', tags=['produtos'])

DBSession = Annotated[Session, Depends(get_session)]


@router.get('/', response_model=list[ProdutoPublico])
def listar_produtos(session: DBSession):
    return session.scalars(
        select(Produto).where(Produto.disponivel.is_(True))
    ).all()


@router.get('/{produto_id}', response_model=ProdutoPublico)
def buscar_produto(produto_id: int, session: DBSession):
    produto = session.scalar(select(Produto).where(Produto.id == produto_id))
    if not produto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado no estoque',
        )
    return produto


@router.post(
    '/',
    response_model=ProdutoPublico,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_usuario_gerente)],
)
def criar_produto(dados: ProdutoSchema, session: DBSession):
    produto = Produto(nome=dados.nome, preco=dados.preco)
    session.add(produto)
    session.commit()
    session.refresh(produto)
    return produto


@router.patch(
    '/{produto_id}',
    response_model=ProdutoPublico,
    dependencies=[Depends(get_usuario_gerente)],
)
def atualizar_produto(
    produto_id: int, dados: ProdutoSchema, session: DBSession
):
    produto = session.scalar(select(Produto).where(Produto.id == produto_id))
    if not produto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado no estoque',
        )

    produto.nome = dados.nome
    produto.preco = dados.preco
    produto.disponivel = dados.disponivel

    session.commit()
    session.refresh(produto)
    return produto


@router.delete(
    '/{produto_id}',
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(get_usuario_gerente)],
)
def desativar_produto(produto_id: int, session: DBSession):
    produto = session.scalar(select(Produto).where(Produto.id == produto_id))
    if not produto:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado no estoque',
        )

    produto.disponivel = False
    session.commit()
