from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import engine
from app.models import Usuario
from app.auth import verificar_senha, hash_senha, criar_token, verificar_token
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

def get_session():
    with Session(engine) as session:
        yield session

def get_usuario_logado(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Usuario:
    dados = verificar_token(token)
    if not dados:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    usuario = session.exec(select(Usuario).where(Usuario.id == dados["sub"])).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return usuario

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    telefone: str
    endereco_cep: str
    endereco_completo: str
    moradia: str
    telas_em_casa: bool
    criancas_em_casa: bool
    area_aberta: bool
    possui_animais: bool
    tipo_animais: str
    qtde_animais: int
    is_admin: bool
    senha: str

class UsuarioRead(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    is_admin: bool

    class Config:
        orm_mode = True

@router.post("/usuarios/", response_model=UsuarioRead)
def criar_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    usuario_existente = session.exec(select(Usuario).where(Usuario.email == usuario.email)).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo_usuario = Usuario(**usuario.dict(exclude={"senha"}))
    novo_usuario.senha = hash_senha(usuario.senha)
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return novo_usuario

@router.post("/usuarios/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == form_data.username)).first()
    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    token = criar_token({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/usuarios/me", response_model=UsuarioRead)
def perfil(usuario: Usuario = Depends(get_usuario_logado)):
    return usuario
