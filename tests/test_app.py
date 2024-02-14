import os

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select

from .conftest import async_session_maker, TstUser
from src.main import app

client = TestClient(app)


def test_check_db_connect():
    response = client.get('/ping/')
    assert response.status_code == 200
    assert response.json() == {'success': True, 'detail': None}


async def test_upload(ac: AsyncClient, user: TstUser):
    tmp = open(os.getcwd() + '/tests/file_to_upload.t', 'rb')
    response = await ac.post('/files/upload', files={'file': ('file_to_upload.t', tmp)}, headers=user.headers)
    tmp.close()
    assert response.status_code == 201
    assert response.json()['id'] == 1
    assert response.json()['filename'] == 'uploads/file_to_upload.t'
    assert response.json()['user_id'] == user.uid


async def test_get_file_list(ac: AsyncClient, user: TstUser):
    response = await ac.get('/files/', headers=user.headers)

    assert response.status_code == 200
    assert response.json()['user_id'] == user.uid
    assert len(response.json()['files']) == 1
    assert response.json()['files'][0]['filename'] == 'uploads/file_to_upload.t'


async def test_download_file(ac: AsyncClient, user: TstUser):
    response = await ac.get('/files/download', params={'file_path': 1}, headers=user.headers)
    assert response.status_code == 200
    
    response = await ac.get('/files/download', params={'file_path': 13}, headers=user.headers)
    assert response.status_code == 404
