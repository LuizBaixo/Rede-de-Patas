from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import engine
from app.models import Ong, Usuario, UsuarioOngAssociacao
from app.routes.usuarios import get_usuario_logado
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

class OngCreate(BaseModel):
    nome: str
    email: str
    telefone: str
    endereco: str
    rede_social: Optional[str] = None
    site: Optional[str] = None

class OngRead(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    endereco: str
    rede_social: Optional[str] = None
    site: Optional[str] = None

    class Config:
        orm_mode = True

class OngUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    rede_social: Optional[str] = None
    site: Optional[str] = None

@router.post("/ongs", response_model=OngRead)
def criar_ong(
    ong: OngCreate,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    if not usuario_logado.is_admin:
        raise HTTPException(status_code=403, detail="Somente administradores podem criar ONGs")

    nova_ong = Ong(**ong.dict())
    session.add(nova_ong)
    session.commit()
    session.refresh(nova_ong)

    associacao = UsuarioOngAssociacao(usuario_id=usuario_logado.id, ong_id=nova_ong.id)
    session.add(associacao)
    session.commit()

    return nova_ong

@router.get("/ongs", response_model=List[OngRead])
def listar_ongs(session: Session = Depends(get_session)):
    return session.exec(select(Ong)).all()

@router.put("/ongs/{ong_id}", response_model=OngRead)
def atualizar_ong(
    ong_id: int,
    dados: OngUpdate,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    permissao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not permissao:
        raise HTTPException(status_code=403, detail="Você não pode editar essa ONG")

    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(ong, key, value)

    session.add(ong)
    session.commit()
    session.refresh(ong)
    return ong

@router.delete("/ongs/{ong_id}/administradores/{admin_id}", status_code=204)
def remover_administrador(
    ong_id: int,
    admin_id: int,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    permissao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not permissao:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover administradores desta ONG")

    associacao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == admin_id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not associacao:
        raise HTTPException(status_code=404, detail="Admin não está associado a essa ONG")

    session.delete(associacao)
    session.commit()

@router.delete("/ongs/{ong_id}", status_code=204)
def excluir_ong(
    ong_id: int,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    permissao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not permissao:
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir essa ONG")

    ong = session.get(Ong, ong_id)
    if not ong:
        raise HTTPException(status_code=404, detail="ONG não encontrada")

    session.exec(
        select(UsuarioOngAssociacao).where(UsuarioOngAssociacao.ong_id == ong_id)
    ).delete()

    session.delete(ong)
    session.commit()

class ConviteAdmin(BaseModel):
    usuario_id: int

@router.post("/ongs/{ong_id}/convidar", status_code=201)
def convidar_administrador(
    ong_id: int,
    convite: ConviteAdmin,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    permissao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not permissao:
        raise HTTPException(status_code=403, detail="Você não tem permissão para convidar nesta ONG")

    usuario_convidado = session.get(Usuario, convite.usuario_id)
    if not usuario_convidado:
        raise HTTPException(status_code=404, detail="Usuário convidado não encontrado")

   
    ja_associado = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == convite.usuario_id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if ja_associado:
        raise HTTPException(status_code=400, detail="Usuário já é administrador dessa ONG")

    nova_associacao = UsuarioOngAssociacao(usuario_id=convite.usuario_id, ong_id=ong_id)
    session.add(nova_associacao)
    session.commit()
    return {"mensagem": "Administrador convidado com sucesso"}

@router.get("/ongs/{ong_id}/administradores", response_model=List[UsuarioRead])
def listar_administradores(
    ong_id: int,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    
    permissao = session.exec(
        select(UsuarioOngAssociacao).where(
            (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
            (UsuarioOngAssociacao.ong_id == ong_id)
        )
    ).first()

    if not permissao:
        raise HTTPException(status_code=403, detail="Você não tem permissão para ver os administradores dessa ONG")

    
    ongs_associacoes = session.exec(
        select(Usuario).join(UsuarioOngAssociacao).where(UsuarioOngAssociacao.ong_id == ong_id)
    ).all()

    return ongs_associacoes
