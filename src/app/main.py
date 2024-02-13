import asyncio
import os
import shutil
import socket
import zipfile
from tarfile import TarFile
from types import NoneType

from asyncpg import exceptions
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, UploadFile, File
from sqlalchemy import select, insert, update, delete, Delete, Update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from .utils import save_file, prepare_full_path, get_file_by_path, get_file_by_id, find_file, get_archive
from ..auth.auth import current_user
from ..core.config import logger, app_settings, ZIP
from ..db.db import get_async_session
from ..main import fastapi_users
from ..models import File, User

router = APIRouter(prefix='/files')
PATH = app_settings.base_upload_dir


@router.post("/upload", tags=["Upload"], status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(),
    path: str = '',
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    if path and path[0] != '/':
        path = '/' + path
    directory = PATH + path
    
    full_path, filename = prepare_full_path(directory, file.filename)

    await save_file(file, full_path, filename)

    file_size = os.path.getsize(f'{full_path}/{filename}')

    new_file = File(
        filename=f'{full_path}/{filename}',
        size=file_size,
        user_id=user.id
    )
    session.add(new_file)
    await session.commit()

    return new_file


# statement = insert(File).values({
#     'filename': f'{full_path}/{filename}',
#     'size': file_size,
#     'user_id': 1
# })
# # await session.execute(statement)

@router.get('/', tags=['Get files list'])
async def get_files(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):
    query = select(File).where(File.user_id == user.id)
    execute = await session.execute(query)
    result = execute.scalars().all()
    return {
        'user_id': user.id,
        'files': result
    }


@router.get("/download", tags=['Download'], status_code=status.HTTP_200_OK)
async def download_file(
    file_path: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    compression: str | None = None
):
    try:
        array = eval(file_path)
    except (NameError, SyntaxError):
        array = None
        
    if compression is None and isinstance(array, (int, NoneType)):
        file = await find_file(session, user, file_path)
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='File not found',
            )
        file_resp = FileResponse(file.filename)
        return file_resp
    
    if compression in ZIP and isinstance(array, (tuple, list)):
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        file_paths = []
        for file_path in array:
            file = await find_file(session, user, file_path)
            if file:
                file_paths.append(file.filename)
                file_name = os.path.basename(file.filename)
                shutil.copyfile(file.filename, os.path.join(temp_dir, file_name))
        if not file_paths:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Files not found',
            )
        
        archive_name = get_archive(file_paths, temp_dir, compression)
        shutil.rmtree(temp_dir)
        return FileResponse(archive_name, filename=archive_name)
        
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Incorrect input parameters',
    )
    
    

