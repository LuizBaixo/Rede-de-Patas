from sqlmodel import Session, select
from app.models import Usuario
from app.schemas import UsuarioCreate


def criar_usuario(db: Session, dados: UsuarioCreate) -> Usuario:
    novo_usuario = Usuario(**dados.dict())
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def listar_usuarios(db: Session) -> list[Usuario]:
    return db.exec(select(Usuario)).all()
