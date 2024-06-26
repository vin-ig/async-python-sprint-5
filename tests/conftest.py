import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import app_settings
from src.db.db import get_async_session
from src.main import app
from src.models.schemas import Base

engine_test = create_async_engine(app_settings.db_dsn_test, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


class TstUser:
    def __init__(self, email: str, password: str, token: str, uid: int):
        self.email = email
        self.password = password
        self.token = token
        self.uid = uid
        self.headers = {'Authorization': f'Bearer {self.token}'}


@pytest.fixture(scope='session')
async def user(ac: AsyncClient) -> TstUser:
    data = {
        "email": "hugo@ya.ru",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": "Hugo"
    }
    crated_user = await ac.post('/auth/register', json=data)
    response = await ac.post(
        '/auth/jwt/login', data={'username': data['email'], 'password': data['password']}
    )
    user_id = crated_user.json()['id']
    token = response.json().get('access_token')
    return TstUser(data['email'], data['password'], token, user_id)
