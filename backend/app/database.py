from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

import os

# Usar ruta absoluta basada en la ubicación de este archivo
# app/database.py -> backend/app/database.py
# Queremos backend/database.db
# O usar variable de entorno DB_PATH si está definida (para Docker)

db_path_env = os.getenv("DB_PATH")
if db_path_env:
    sqlite_file_name = Path(db_path_env)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    sqlite_file_name = BASE_DIR / "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
