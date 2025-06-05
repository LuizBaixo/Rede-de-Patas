from sqlmodel import SQLModel, create_engine
from app.models import Usuario

DATABASE_URL = "postgresql://rede_user:653296@localhost:5432/rede_de_patas"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
