from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import engine
from app.models import Animal, Usuario, UsuarioOngAssociacao
from typing import List, Optional
from pydantic import BaseModel
from app.routes.usuarios import get_usuario_logado

router = APIRouter()

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
    ong_id: Optional[int] = None

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
    ong_id: Optional[int] = None

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/animais", response_model=AnimalRead)
def criar_animal(
    animal: AnimalCreate,
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    if not usuario_logado.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar animais")

    if animal.ong_id:
        permissao = session.exec(
            select(UsuarioOngAssociacao).where(
                (UsuarioOngAssociacao.usuario_id == usuario_logado.id) &
                (UsuarioOngAssociacao.ong_id == animal.ong_id)
            )
        ).first()
        if not permissao:
            raise HTTPException(status_code=403, detail="Você não tem permissão para cadastrar animal nessa ONG")

    novo_animal = Animal.from_orm(animal)
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
def atualizar_animal(animal_id: int, dados: AnimalUpdate, session: Session = Depends(get_session)):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    for key, value in dados.dict(exclude_unset=True).items():
        setattr(animal, key, value)

    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal

@router.delete("/animais/{animal_id}", status_code=204)
def deletar_animal(animal_id: int, session: Session = Depends(get_session)):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    session.delete(animal)
    session.commit()

@router.get("/animais/minhas-ongs", response_model=List[AnimalRead])
def listar_animais_das_minhas_ongs(
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session),
):
    if not usuario_logado.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem ver seus animais")

    ongs_ids = [
        assoc.ong_id for assoc in session.exec(
            select(UsuarioOngAssociacao).where(UsuarioOngAssociacao.usuario_id == usuario_logado.id)
        ).all()
    ]

    if not ongs_ids:
        return []

    animais = session.exec(
        select(Animal).where(Animal.ong_id.in_(ongs_ids))
    ).all()

    return animais
