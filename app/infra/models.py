from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    registry,
    relationship,
)

from app.schemas import (
    CanalPedido,
    PerfilUsuario,
    StatusPagamento,
    StatusPedido,
    TipoMovimentacao,
)

table_registry = registry()


@table_registry.mapped_as_dataclass
class Usuario:
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    senha: Mapped[str] = mapped_column(String(50))
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(PerfilUsuario, native_enum=False), default=PerfilUsuario.CLIENTE
    )
    consentimento_lgpd: Mapped[bool] = mapped_column(default=False)
    criado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    pedidos: Mapped[List['Pedido']] = relationship(
        back_populates='cliente', init=False
    )
    fidelidade: Mapped[Optional['Fidelidade']] = relationship(
        back_populates='usuario', init=False
    )


@table_registry.mapped_as_dataclass
class Unidade:
    __tablename__ = 'unidades'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str] = mapped_column(String(80))
    cidade: Mapped[str] = mapped_column(String(80))
    endereco: Mapped[str] = mapped_column(String(80))
    aberta: Mapped[bool] = mapped_column(default=True)

    estoques: Mapped[List['Estoque']] = relationship(
        back_populates='unidade', init=False
    )
    pedidos: Mapped[List['Pedido']] = relationship(
        back_populates='unidade', init=False
    )


@table_registry.mapped_as_dataclass
class Produto:
    __tablename__ = 'produtos'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome: Mapped[str] = mapped_column(String(50))
    preco: Mapped[float] = mapped_column(Numeric(10, 2))
    disponivel: Mapped[bool] = mapped_column(default=True)

    estoques: Mapped[List['Estoque']] = relationship(
        back_populates='produto', init=False
    )
    itens_pedido: Mapped[List['ItemPedido']] = relationship(
        back_populates='produto', init=False
    )


@table_registry.mapped_as_dataclass
class Estoque:
    __tablename__ = 'estoques'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey('unidades.id'))
    produto_id: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    quantidade: Mapped[int] = mapped_column(default=0)

    unidade: Mapped['Unidade'] = relationship(
        back_populates='estoques', init=False
    )
    produto: Mapped['Produto'] = relationship(
        back_populates='estoques', init=False
    )
    movimentacoes: Mapped[List['MovimentacaoEstoque']] = relationship(
        back_populates='estoque', init=False
    )


@table_registry.mapped_as_dataclass
class MovimentacaoEstoque:
    __tablename__ = 'movimentacoes_estoque'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    estoque_id: Mapped[int] = mapped_column(ForeignKey('estoques.id'))
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(TipoMovimentacao, native_enum=False)
    )
    quantidade: Mapped[int] = mapped_column()
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    estoque: Mapped['Estoque'] = relationship(
        back_populates='movimentacoes', init=False
    )


@table_registry.mapped_as_dataclass
class Pedido:
    __tablename__ = 'pedidos'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    unidade_id: Mapped[int] = mapped_column(ForeignKey('unidades.id'))
    canal: Mapped[CanalPedido] = mapped_column(
        Enum(CanalPedido, native_enum=False)
    )
    status: Mapped[StatusPedido] = mapped_column(
        Enum(StatusPedido, native_enum=False),
        default=StatusPedido.AGUARDANDO_PAGAMENTO,
    )
    total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    criado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    cliente: Mapped['Usuario'] = relationship(
        back_populates='pedidos', init=False
    )
    unidade: Mapped['Unidade'] = relationship(
        back_populates='pedidos', init=False
    )
    itens: Mapped[List['ItemPedido']] = relationship(
        back_populates='pedido', init=False
    )
    pagamento: Mapped[Optional['Pagamento']] = relationship(
        back_populates='pedido', init=False
    )


@table_registry.mapped_as_dataclass
class ItemPedido:
    __tablename__ = 'itens_pedido'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    pedido_id: Mapped[int] = mapped_column(ForeignKey('pedidos.id'))
    produto_id: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    quantidade: Mapped[int] = mapped_column()
    preco_unitario: Mapped[float] = mapped_column(Numeric(10, 2))

    pedido: Mapped['Pedido'] = relationship(back_populates='itens', init=False)
    produto: Mapped['Produto'] = relationship(
        back_populates='itens_pedido', init=False
    )


@table_registry.mapped_as_dataclass
class Pagamento:
    __tablename__ = 'pagamentos'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey('pedidos.id'), unique=True
    )
    forma_pagamento: Mapped[str] = mapped_column(String(50))
    status: Mapped[StatusPagamento] = mapped_column(
        Enum(StatusPagamento, native_enum=False),
        default=StatusPagamento.PENDENTE,
    )
    payload_retorno: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None
    )
    criado_em: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    pedido: Mapped['Pedido'] = relationship(
        back_populates='pagamento', init=False
    )


@table_registry.mapped_as_dataclass
class Fidelidade:
    __tablename__ = 'fidelidade'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id'), unique=True
    )
    pontos: Mapped[int] = mapped_column(default=0)
    consentimento: Mapped[bool] = mapped_column(default=False)

    usuario: Mapped['Usuario'] = relationship(
        back_populates='fidelidade', init=False
    )
