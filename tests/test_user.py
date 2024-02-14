from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select

from .conftest import async_session_maker
from src.main import app

client = TestClient(app)


async def test_register_user(ac: AsyncClient):
    response = await ac.post('/auth/register', json={
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": "string"
    })
    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "email": "user@example.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": "string"
    }

    # Повторное создание такого же пользователя
    response = await ac.post('/auth/register', json={
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": "string"
    })
    assert response.status_code == 400
    assert response.json() == {
        "detail": "REGISTER_USER_ALREADY_EXISTS"
    }

    # Неверный запрос
    response = await ac.post('/auth/register', json={
        "email": "user_2@example.com",
    })
    assert response.status_code == 422
