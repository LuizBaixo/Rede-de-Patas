from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import engine
from app.models import Ong, Usuario, UsuarioOngAssociacao
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class OngBase(BaseModel):
    nome: str
    email: str
    telefone: str
    endereco: str
    rede_social: Optional[str] = None
    site: Optional[str] = None


class OngCreate(OngBase):
    pass


class OngRead(OngBase):
    id: int

    class Config:
        orm_mode = True


class OngUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    rede_social: Optional[str] = None
    site: Optional[str] = None


class AdministradorAssociacao(BaseModel):
    usuario_id: int


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/ongs", response_model=OngRead)
def criar_ong(ong: OngCreate, session: Session = Depends(get_session)):
    nova_ong = Ong.from_orm(ong)
    session.add(nova_ong)
    session.commit()
    session.refresh(nova_ong)
    return nova_ong


@router.get("/ongs", response_model=List[OngRead])
def listar_ongs(session: Session = Depends(get_session)):
    ongs = session.exec(select(Ong)).all()
    return ongs


@router.get("/ongs/{ong_id}", response_model=OngRead)
def obter_ong(ong_id: int, session: Session = Depends(get_session)):
    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")
    return ong


@router.put("/ongs/{ong_id}", response_model=OngRead)
def atualizar_ong(ong_id: int, dados: OngUpdate, session: Session = Depends(get_session)):
    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(ong, key, value)

    session.add(ong)
    session.commit()
    session.refresh(ong)
    return ong


@router.delete("/ongs/{ong_id}", status_code=204)
def deletar_ong(ong_id: int, session: Session = Depends(get_session)):
    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")
    session.delete(ong)
    session.commit()


@router.post("/ongs/{ong_id}/administradores", status_code=204)
def adicionar_administrador(ong_id: int, assoc: AdministradorAssociacao, session: Session = Depends(get_session)):
    ong = session.get(Ong, ong_id)
    usuario = session.get(Usuario, assoc.usuario_id)

    if not ong or not usuario:
        raise HTTPException(status_code=404, detail="ONG ou usuário não encontrado")

    if not usuario.is_admin:
        raise HTTPException(status_code=400, detail="Usuário não é um administrador")

    relacao = UsuarioOngAssociacao(usuario_id=usuario.id, ong_id=ong.id)
    session.add(relacao)
    session.commit()


@router.get("/ongs/{ong_id}/administradores", response_model=List[str])
def listar_administradores(ong_id: int, session: Session = Depends(get_session)):
    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")
    return [admin.nome for admin in ong.administradores]
