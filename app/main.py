from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.unidades import router as unidades_router
from app.routers.users import router as users_router
from app.settings import Settings

settings = Settings()

app = FastAPI(
    title='Raízes do Nordeste API',
    version='1.0.0',
    description='API para rede de lanchonetes Raízes do Nordeste',
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(unidades_router)


@app.get('/')
def root():
    return {'message': 'Teste, API funcionando!'}
