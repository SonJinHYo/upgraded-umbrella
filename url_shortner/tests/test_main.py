import os
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


cwd = os.path.dirname(__file__)
base_dir = os.path.dirname(os.path.dirname(cwd))

sys.path.append(base_dir)

from url_shortner.main import app, get_db
from url_shortner.database import Base
from url_shortner.schemas import ExpirationDate


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_shorten_url():
    for expiry_val in ExpirationDate:
        response = client.post("/shorten", json={"url": f"https://www.example.com/{expiry_val}", "expiry": expiry_val.value})
        assert response.status_code == 200
        assert "short_url" in response.json()
    
    response = client.post("/shorten", json={"url": f"https://www.example.com/", "expiry": "asdas"})
    assert response.status_code == 422


def test_redirect_url():
    response = client.post("/shorten", json={"url": "https://www.example.com", "expiry": "1 day"})
    assert response.status_code == 200
    
    short_url: str = response.json()['short_url']
    short_key = short_url.split('/')[-1]
    response = client.get(f"/{short_key}")
    assert response.status_code == 404

    response = client.get(f"/wrongkey12")
    assert response.status_code == 404
