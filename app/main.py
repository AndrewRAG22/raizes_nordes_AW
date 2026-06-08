from fastapi import FastAPI

app = FastAPI(
    title='Raízes do Nordeste API',
    version='1.0.0',
)


@app.get('/')
async def root():
    return {'message': 'Raízes do Nordeste API'}
