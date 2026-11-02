from sqlalchemy import create_engine, event
from sqlmodel import SQLModel, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Aplica directivas normativas de SQLite WAL y concurrencia."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA busy_timeout=10000;")
    cursor.close()

def create_db_and_tables():
    """Crea las tablas definidas si no existen."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Generador de sesión para inyección de dependencias."""
    with Session(engine) as session:
        yield session
