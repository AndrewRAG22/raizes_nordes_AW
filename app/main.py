from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.routers.estoque import router as estoque_router
from app.routers.fidelidade import router as fidelidade_router
from app.routers.pagamentos import router as pagamentos_router
from app.routers.pedidos import router as pedidos_router
from app.routers.produtos import router as produtos_router
from app.routers.unidades import router as unidades_router
from app.routers.users import router as users_router
from app.settings import Settings

settings = Settings()

HTTP_ERROR_CODES = {
    400: 'BAD_REQUEST',
    401: 'NAO_AUTENTICADO',
    403: 'SEM_PERMISSAO',
    404: 'NAO_ENCONTRADO',
    409: 'CONFLITO',
    422: 'DADOS_INVALIDOS',
}

app = FastAPI(
    title='Raízes do Nordeste API',
    version='1.0.0',
    description='API para rede de lanchonetes Raízes do Nordeste',
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': HTTP_ERROR_CODES.get(
                exc.status_code,
                'ERRO_NEGOCIO',
            ),
            'message': exc.detail,
            'details': [],
            'timestamp': datetime.now(tz=ZoneInfo('UTC')).isoformat(),
            'path': request.url.path,
        },
    )


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(unidades_router)
app.include_router(produtos_router)
app.include_router(estoque_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)
app.include_router(fidelidade_router)


@app.get('/')
def root():
    return {'message': 'Teste, API funcionando!'}
