from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

class UsuarioOngAssociacao(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    ong_id: Optional[int] = Field(default=None, foreign_key="ong.id", primary_key=True)

class Ong(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str
    telefone: str
    endereco: str
    rede_social: Optional[str] = None
    site: Optional[str] = None

    administradores: List["Usuario"] = Relationship(back_populates="ongs", link_model=UsuarioOngAssociacao)

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    is_admin: bool
    senha: str
    ong_id: Optional[int] = Field(default=None, foreign_key="ong.id")

    ongs: List["Ong"] = Relationship(back_populates="administradores", link_model=UsuarioOngAssociacao)

class Animal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    ong_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
