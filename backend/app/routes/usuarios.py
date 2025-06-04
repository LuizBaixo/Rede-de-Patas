from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schemas import UsuarioCreate, UsuarioRead
from app.crud import criar_usuario, listar_usuarios
from app.database import engine

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/", response_model=UsuarioRead)
def criar(dados: UsuarioCreate, db: Session = Depends(get_session)):
    return criar_usuario(db, dados)

@router.get("/", response_model=list[UsuarioRead])
def listar(db: Session = Depends(get_session)):
    return listar_usuarios(db)
