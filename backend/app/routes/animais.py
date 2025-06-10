import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from app.database import engine
from app.models import Animal, Usuario
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
def criar_animal(animal: AnimalCreate, session: Session = Depends(get_session)):
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


@router.post("/animais/{animal_id}/upload_foto")
def upload_foto_animal(
    animal_id: int,
    arquivo: UploadFile = File(...),
    usuario_logado: Usuario = Depends(get_usuario_logado),
    session: Session = Depends(get_session)
):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    if animal.ong_id not in [ong.id for ong in usuario_logado.ongs]:
        raise HTTPException(status_code=403, detail="Sem permissão para esse animal")

    pasta = "uploads"
    os.makedirs(pasta, exist_ok=True)

    ext = os.path.splitext(arquivo.filename)[1]
    nome_arquivo = f"{uuid4()}{ext}"
    caminho = os.path.join(pasta, nome_arquivo)

    with open(caminho, "wb") as buffer:
        buffer.write(arquivo.file.read())

    animal.foto_url = f"/uploads/{nome_arquivo}"
    session.add(animal)
    session.commit()
    session.refresh(animal)

    return {"foto_url": animal.foto_url}
