import os
import random
import sys

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

cwd = os.path.dirname(__file__)
base_dir = os.path.dirname(os.path.dirname(cwd))

sys.path.append(base_dir)

from url_shortner.schemas import ExpirationDate
from url_shortner.database import Base
from url_shortner.main import app
from url_shortner.utils import get_db


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    )


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="module")
async def setup_and_teardown_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.anyio
async def test_shorten_url(setup_and_teardown_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for expiry_val in ExpirationDate:
            response = await client.post(
                "/shorten", json={"url": f"https://www.example.com/{expiry_val}", "expiry": expiry_val.value}
            )
            assert response.status_code == 200
            assert "short_url" in response.json()

        response = await client.post("/shorten", json={"url": f"https://www.example.com/", "expiry": "asdas"})
        assert response.status_code == 422


@pytest.mark.anyio
async def test_redirect_url(setup_and_teardown_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={"url": "https://www.example.com", "expiry": "1 day"})
        assert response.status_code == 200

        short_url = response.json()['short_url']
        short_key = short_url.split('/')[-1]
        response = await client.get(f"/{short_key}")
        assert response.status_code == 301

        response = await client.get(f"/wrongkey12")
        assert response.status_code == 404


@pytest.mark.anyio
async def test_click_stats_url(setup_and_teardown_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={"url": f"https://www.example.{random.choices('unique', k=6)}", "expiry": "1 day"})
        assert response.status_code == 200

        short_url = response.json()['short_url']
        short_key = short_url.split('/')[-1]

        clicks_cnt = 100

        for _ in range(clicks_cnt):
            await client.get(f"/{short_key}")

        response = await client.get(f"/stats/{short_key}")
        response_clicks = response.json()["clicks"]

        assert response_clicks == clicks_cnt
