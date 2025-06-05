# app/security.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select
from app.database import engine
from app.auth import verificar_token
from app.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_usuario_logado(token: str = Depends(oauth2_scheme)) -> Usuario:
    dados = verificar_token(token)
    if not dados or "sub" not in dados:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = int(dados["sub"])
    with Session(engine) as session:
        usuario = session.get(Usuario, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return usuario
