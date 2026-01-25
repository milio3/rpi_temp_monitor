from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Usar variable de entorno DB_PATH si está definida, sino usar settings
# Pero settings ya maneja el default.
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
