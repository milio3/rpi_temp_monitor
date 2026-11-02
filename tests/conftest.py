from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine
from starlette.testclient import TestClient

from app.core.database import get_session
from app.main import app
from app.models.reading import TemperatureReading

# Motor aislado exclusivamente en memoria para evitar polución de datos
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session", scope="function")
def session_fixture():
    """Genera una sesión limpia en memoria con tablas y datos semilla de prueba."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        # Datos semilla de prueba aislados
        now = datetime.now(timezone.utc)
        r1 = TemperatureReading(temperature=42.0, timestamp=now - timedelta(hours=5))
        r2 = TemperatureReading(temperature=48.5, timestamp=now - timedelta(hours=2))
        r3 = TemperatureReading(temperature=52.3, timestamp=now)
        session.add_all([r1, r2, r3])
        session.commit()
        yield session

    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session):
    """Proporciona un TestClient con la dependencia de base de datos anulada."""
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
