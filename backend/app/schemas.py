from typing import Optional
from sqlmodel import SQLModel


class UsuarioBase(SQLModel):
    nome: str
    email: str
    telefone: str
    endereco_cep: str
    endereco_completo: str
    moradia: Optional[str] = None
    telas_em_casa: Optional[bool] = None
    criancas_em_casa: Optional[bool] = None
    area_aberta: Optional[bool] = None
    possui_animais: Optional[bool] = None
    tipo_animais: Optional[str] = None
    qtde_animais: Optional[int] = None
    is_admin: bool = False
    ong_id: Optional[int] = None


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioRead(UsuarioBase):
    id: int
