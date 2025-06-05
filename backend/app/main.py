from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routes import usuarios, animais, ongs, auth 

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(usuarios.router)
app.include_router(animais.router)
app.include_router(ongs.router)
app.include_router(auth.router)   

@app.get("/")
def read_root():
    return {"message": "Rede de Patas API está online!"}
