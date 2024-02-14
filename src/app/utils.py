import os
import tarfile
import zipfile

from py7zr import SevenZipFile
from sqlalchemy import select, and_

from src.core.config import app_settings
from src.models import File
import py7zr


async def get_file_by_id(session, user, file_id):
    query = select(File).where(and_(File.id == file_id, File.user_id == user.id))
    execute = await session.execute(query)
    return execute.scalars().all()


async def get_file_by_path(session, user, path):
    query = select(File).where(and_(File.filename == path, File.user_id == user.id))
    execute = await session.execute(query)
    return execute.scalars().all()


async def save_file(file, path, filename):
    if path and path[-1] != '/':
        path += '/'
    path = path.lstrip('/')
    os.makedirs(path, exist_ok=True)
    with open(path + filename, 'wb') as upload_file:
        file_content = await file.read()
        upload_file.write(file_content)


def prepare_full_path(path, filename):
    path = path.strip('/')
    parts = path.rsplit('/', 1)
    if '.' in parts[-1]:
        return parts
    return [path, filename]


async def find_file(session, user, file_path):
    try:
        file_id = int(file_path)
    except ValueError:
        file_id = None
    
    if file_id is None:
        file = await get_file_by_path(session, user, file_path)
    else:
        file = await get_file_by_id(session, user, file_id)
    return file[0] if len(file) == 1 else None


def get_archive(file_paths, compression):
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
