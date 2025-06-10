from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import engine
from app.models import Animal, UsuarioOngAssociacao
from typing import List, Optional
from pydantic import BaseModel
from app.routes.usuarios import get_usuario_logado
from app.models import Usuario

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

class AnimalBase(BaseModel):
    nome: str
    idade: Optional[int] = None
    especie: str
    raca: Optional[str] = None
    porte: Optional[str] = None
    cor: Optional[str] = None
    vacinado: Optional[bool] = None
    castrado: Optional[bool] = None
    vermifugado: Optional[bool] = None
    sexo: Optional[str] = None
    descricao: Optional[str] = None
    disponivel: Optional[bool] = True
    sociavel_com_gatos: Optional[bool] = None
    sociavel_com_caes: Optional[bool] = None

class AnimalCreate(AnimalBase):
    pass  # ong_id será definido automaticamente

class AnimalRead(AnimalBase):
    id: int
    ong_id: Optional[int]

    class Config:
        orm_mode = True

class AnimalUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    especie: Optional[str] = None
    raca: Optional[str] = None
    porte: Optional[str] = None
    cor: Optional[str] = None
    vacinado: Optional[bool] = None
    castrado: Optional[bool] = None
    vermifugado: Optional[bool] = None
    sexo: Optional[str] = None
    descricao: Optional[str] = None
    disponivel: Optional[bool] = None
    sociavel_com_gatos: Optional[bool] = None
    sociavel_com_caes: Optional[bool] = None

@router.post("/animais", response_model=AnimalRead)
def criar_animal(
    animal: AnimalCreate,
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(get_usuario_logado)
):
    if not usuario_logado.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem cadastrar animais")

    # Buscar uma ONG que o admin logado está associado
    associacao = session.exec(
        select(UsuarioOngAssociacao).where(UsuarioOngAssociacao.usuario_id == usuario_logado.id)
    ).first()

    if not associacao:
        raise HTTPException(status_code=403, detail="Você não está associado a nenhuma ONG")

    novo_animal = Animal(**animal.dict(), ong_id=associacao.ong_id)
    session.add(novo_animal)
    session.commit()
    session.refresh(novo_animal)
    return novo_animal

@router.get("/animais", response_model=List[AnimalRead])
def listar_animais(
    disponivel: Optional[bool] = Query(None),
    sociavel_com_gatos: Optional[bool] = Query(None),
    sociavel_com_caes: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(Animal)
    if disponivel is not None:
        query = query.where(Animal.disponivel == disponivel)
    if sociavel_com_gatos is not None:
        query = query.where(Animal.sociavel_com_gatos == sociavel_com_gatos)
    if sociavel_com_caes is not None:
        query = query.where(Animal.sociavel_com_caes == sociavel_com_caes)

    animais = session.exec(query).all()
    return animais

@router.get("/animais/{animal_id}", response_model=AnimalRead)
def obter_animal(animal_id: int, session: Session = Depends(get_session)):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

@router.put("/animais/{animal_id}", response_model=AnimalRead)
def atualizar_animal(
    animal_id: int,
    dados: AnimalUpdate,
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(get_usuario_logado)
):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    if not usuario_logado.is_admin or animal.ong_id not in [
        assoc.ong_id for assoc in session.exec(
            select(UsuarioOngAssociacao).where(UsuarioOngAssociacao.usuario_id == usuario_logado.id)
        ).all()
    ]:
        raise HTTPException(status_code=403, detail="Você não pode atualizar este animal")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(animal, key, value)

    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal

@router.delete("/animais/{animal_id}", status_code=204)
def deletar_animal(
    animal_id: int,
    session: Session = Depends(get_session),
    usuario_logado: Usuario = Depends(get_usuario_logado)
):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    if not usuario_logado.is_admin or animal.ong_id not in [
        assoc.ong_id for assoc in session.exec(
            select(UsuarioOngAssociacao).where(UsuarioOngAssociacao.usuario_id == usuario_logado.id)
        ).all()
    ]:
        raise HTTPException(status_code=403, detail="Você não pode deletar este animal")

    session.delete(animal)
    session.commit()
