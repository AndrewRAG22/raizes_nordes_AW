from sqlalchemy.orm import Session

from app.infra.models import LogAuditoria


def registrar_log(
    session: Session,
    acao: str,
    usuario_id: int | None = None,
    detalhe: str | None = None,
):
    log = LogAuditoria(
        usuario_id=usuario_id,
        acao=acao,
        detalhe=detalhe,
    )
    session.add(log)
