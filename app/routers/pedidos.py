from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database import get_session
from app.infra.logs import registrar_log
from app.infra.models import (
    Estoque,
    ItemPedido,
    Pedido,
    Produto,
    Unidade,
    Usuario,
)
from app.infra.security import get_current_user
from app.schemas import AtualizarStatusSchema, PedidoPublico, PedidoSchema
from app.schemas.enums import StatusPedido

router = APIRouter(prefix='/pedidos', tags=['pedidos'])

DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.post('/', response_model=PedidoPublico, status_code=HTTPStatus.CREATED)
def criar_pedido(
    dados: PedidoSchema, session: DBSession, usuario: CurrentUser
):
    unidade = session.scalar(
        select(Unidade).where(Unidade.id == dados.unidade_id)
    )
    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não foi encontrada',
        )

    total = 0.0
    itens = []

    for item in dados.itens:
        produto = session.scalar(
            select(Produto).where(Produto.id == item.produto_id)
        )
        if not produto:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='O Produto não foi encontrado',
            )

        estoque = session.scalar(
            select(Estoque).where(
                Estoque.unidade_id == dados.unidade_id,
                Estoque.produto_id == item.produto_id,
            )
        )
        if not estoque or estoque.quantidade < item.quantidade:
            disponivel = estoque.quantidade if estoque else 0
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f'O {produto.nome} só tem {disponivel} em estoque',
            )
        total += float(produto.preco) * item.quantidade
        itens.append((produto, item.quantidade, estoque))

    pedido = Pedido(
        cliente_id=usuario.id,
        unidade_id=dados.unidade_id,
        canal=dados.canal,
        total=total,
    )
    session.add(pedido)
    session.flush()

    for produto, quantidade, estoque in itens:
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
        )
        session.add(item_pedido)

        estoque.quantidade -= quantidade

    registrar_log(
        session,
        'Pedido Criado',
        usuario.id,
        f'Pedido {pedido.id} realizado no canal {dados.canal} criado',
    )

    session.commit()
    session.refresh(pedido)

    return pedido


@router.get('/', response_model=list[PedidoPublico])
def listar_pedidos(
    session: DBSession,
    usuario: CurrentUser,
    canalPedido: str | None = None,
    status: str | None = None,
):
    query = select(Pedido).where(Pedido.cliente_id == usuario.id)

    if canalPedido:
        query = query.where(Pedido.canal == canalPedido)
    if status:
        query = query.where(Pedido.status == status)

    return session.scalars(query).all()


@router.get('/{pedido_id}', response_model=PedidoPublico)
def buscar_pedido(pedido_id: int, session: DBSession, usuario: CurrentUser):
    pedido = session.scalar(
        select(Pedido).where(
            Pedido.id == pedido_id,
            Pedido.cliente_id == usuario.id,
        )
    )
    if not pedido:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Pedido não encontrado',
        )
    return pedido


@router.patch('/{pedido_id}/status', response_model=PedidoPublico)
def atualizar_status(
    pedido_id: int,
    dados: AtualizarStatusSchema,
    session: DBSession,
    usuario: CurrentUser,
):
    pedido = session.scalar(
        select(Pedido).where(
            Pedido.id == pedido_id, Pedido.cliente_id == usuario.id
        )
    )
    if not pedido:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Pedido não encontrado ou sem permissão para alterar',
        )

    if pedido.status == StatusPedido.CANCELADO:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Pedido está cancelado',
        )

    pedido.status = dados.status
    registrar_log(
        session,
        'Pedido alterado',
        usuario.id,
        f'Pedido {pedido_id} foi alterado para o status {dados.status}',
    )

    session.commit()
    session.refresh(pedido)
    return pedido


@router.delete('/{pedido_id}', status_code=HTTPStatus.NO_CONTENT)
def cancelar_pedido(pedido_id: int, session: DBSession, usuario: CurrentUser):
    pedido = session.scalar(
        select(Pedido).where(
            Pedido.id == pedido_id,
            Pedido.cliente_id == usuario.id,
        )
    )
    if not pedido:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Pedido não encontrado ou sem permissão para cancelar',
        )

    if pedido.status not in (StatusPedido.AGUARDANDO_PAGAMENTO):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Só é possível cancelar pedidos aguardando pagamento',
        )

    pedido.status = StatusPedido.CANCELADO
    registrar_log(
        session,
        'Pedido Cancelado',
        usuario.id,
        f'Pedido {pedido_id} foi cancelado com sucesso',
    )
    session.commit()
