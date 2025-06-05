# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.models import Usuario
from app.database import engine
from app.auth import verificar_senha, criar_token

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.email == form_data.username)).first()

        if not usuario or not verificar_senha(form_data.password, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = criar_token(data={"sub": str(usuario.id)})

        return {"access_token": access_token, "token_type": "bearer"}
