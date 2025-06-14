from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select
from app.database import engine
from app.models import Animal, Usuario, UsuarioOngAssociacao
from typing import List, Optional
from pydantic import BaseModel
from app.routes.usuarios import get_usuario_logado
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "app/static/animais"

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
    foto_url: Optional[str] = None

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
    foto_url: Optional[str] = None
    ong_id: Optional[int] = None

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/animais", response_model=AnimalRead)
def criar_animal(
    animal: AnimalCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_usuario_logado)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar animais.")

    novo_animal = Animal.from_orm(animal)
    novo_animal.ong_id = usuario.id  
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

    return session.exec(query).all()

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

@router.put("/animais/{animal_id}/foto", response_model=AnimalRead)
def atualizar_foto_animal(
    animal_id: int,
    arquivo: UploadFile = File(...),
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_usuario_logado)
):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar a imagem")

    filename = f"animal_{animal_id}_{arquivo.filename}"
    caminho_completo = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    animal.foto_url = f"/static/animais/{filename}"
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
