import os
os.environ["DATABASE_URL"]="sqlite:///./test_sungai.db"
os.environ["MQTT_ENABLED"]="false"
import pytest
from fastapi.testclient import TestClient
from app.db import Base,engine
from app.main import app
from app.seed import seed
@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); seed()
    with TestClient(app) as c: yield c
