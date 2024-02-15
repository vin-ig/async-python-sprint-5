import os
import tarfile
import zipfile

import aiofiles
import py7zr
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import app_settings
from src.models import File, User


async def get_file_by_id(session: AsyncSession, user: User, file_id: int) -> list[File]:
    """ Возвращает файлы по id """
    query = select(File).where(and_(File.id == file_id, File.user_id == user.id))
    execute = await session.execute(query)
    return execute.scalars().all()


async def get_file_by_path(session: AsyncSession, user: User, path: str) -> list[File]:
    """ Возвращает файлы по пути """
    query = select(File).where(and_(File.filename == path, File.user_id == user.id))
    execute = await session.execute(query)
    return execute.scalars().all()


async def find_file(session: AsyncSession, user: User, file_path: str) -> File:
    """ Ищет файл по id или пути """
    try:
        file_id = int(file_path)
    except ValueError:
        file_id = None

    if file_id is None:
        file = await get_file_by_path(session, user, file_path)
    else:
        file = await get_file_by_id(session, user, file_id)
    return file[0] if len(file) == 1 else None


async def save_file(file: File, path: str, filename: str) -> None:
    """ Сохраняет файл в хранилище """
    if path and path[-1] != '/':
        path += '/'
    path = path.lstrip('/')
    os.makedirs(path, exist_ok=True)
    chunk_size = 1024
    async with aiofiles.open(path + filename, 'wb') as upload_file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await upload_file.write(chunk)


def prepare_full_path(path: str, filename: str) -> list[str]:
    """ Возвращает обработанный путь файла """
    path = path.strip('/')
    parts = path.rsplit('/', 1)
    if '.' in parts[-1]:
        return parts
    return [path, filename]


def get_archive(file_paths: list[str], compression: str) -> str:
    """ Создает архив с файлами для скачивания и возвращает его имя """
    archive_file = f'{app_settings.arch_dir}/archive.{compression}'
    if compression == 'zip':
        with zipfile.ZipFile(archive_file, 'w') as zip_file:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                zip_file.write(os.path.join(app_settings.temp_dir, file_name), file_name)
        return zip_file.filename
    elif compression == '7z':
        with py7zr.SevenZipFile(archive_file, 'w') as szf:
            for path in file_paths:
                szf.write(path)
        return szf.filename
    elif compression == 'tar':
        with tarfile.open(archive_file, 'w') as tar:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                tar.add(os.path.join(app_settings.temp_dir, file_name), arcname=file_name)
        return tar.name
