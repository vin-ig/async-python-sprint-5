import asyncio
import socket

from asyncpg import exceptions
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select, insert, update, delete, Delete, Update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import logger
from ..db.db import get_async_session

router = APIRouter()


@router.get('/')
def index(session: AsyncSession = Depends(get_async_session)):
    return {'msg': 'hello'}

# @router.post('/', response_model=list[ShortUrl], status_code=status.HTTP_201_CREATED)
# async def add_new_url(urls: list[OriginalUrl], session: AsyncSession = Depends(get_async_session)):
#     """ Добавляет новые url в БД """
#     to_return = []
#     to_create = []
#     exist_urls = await get_exist_url(session, urls)
#     for url in urls:
#         if url.original_url not in exist_urls:
#             to_create.append({
#                 'short_url': get_hash(url.original_url),
#                 'original_url': url.original_url,
#                 'active': True
#             })
#         else:
#             exist = exist_urls[url.original_url]
#             to_return.append({
#                 'id': exist.id,
#                 'short_url': exist.short_url,
#                 'original_url': exist.original_url,
#                 'active': exist.active
#             })
#     if to_create:
#         statement = insert(ShortUrlSchema).values(to_create).returning(ShortUrlSchema.id)
#         result = await session.execute(statement)
#         await session.commit()
#         result_ids = [row_id[0] for row_id in result]
#         for i in range(len(to_create)):
#             to_create[i]['id'] = result_ids[i]
#     return to_create + to_return
#
#
# @router.get('/{short_url}')
# async def get_original_url(short_url: str, request: Request, session: AsyncSession = Depends(get_async_session)):
#     """ Осуществляет переход по сокращенной ссылке """
#     query = select(ShortUrlSchema).where(ShortUrlSchema.short_url == short_url)
#     execute = await session.execute(query)
#     result = execute.scalars().all()
#     if not result:
#         logger.info(f'[get_original_url()] 404: {short_url}')
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Record does not exist',
#         )
#
#     if not result[0].active:
#         logger.info(f'[get_original_url] 410: {short_url}')
#         raise HTTPException(
#             status_code=status.HTTP_410_GONE,
#             detail='Record has been deleted',
#         )
#
#     statement = insert(TransitionSchema).values({
#         'url_id': result[0].id,
#         'client_info': {
#             'host': request.client.host if request.client else None,
#             'port': request.client.port if request.client else None,
#             'headers': dict(request.headers),
#         }
#     })
#     await session.execute(statement)
#     await session.commit()
#
#     return Response(status_code=307, headers={'Location': result[0].original_url})
#
#
# @router.get('/status/{uid}')
# async def get_status(
#         uid: int,
#         detail=None,
#         limit: int = 10,
#         offset: int = 0,
#         session: AsyncSession = Depends(get_async_session)
# ):
#     """ Отдает статистику переходов по сокращенной ссылке """
#
#     # Смотрим, есть ли такой url в БД
#     exist_url = await session.get(ShortUrlSchema, uid)
#     if not exist_url:
#         logger.info(f'[get_status()] 404: {uid}')
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Record does not exist',
#         )
#
#     query = select(TransitionSchema).where(TransitionSchema.url_id == uid)
#     execute = await session.execute(query)
#     transitions = execute.scalars().all()
#     result = {'transitions': len(transitions)}
#     if detail is None:
#         return result
#
#     detail = []
#     for tr in transitions:
#         detail.append({
#             'click_date': tr.click_date,
#             'client_info': tr.client_info,
#         })
#     result['detail'] = detail[offset:][:limit]
#     return result
#
#
# @router.delete('/{short_url}', response_model=ShortUrl)
# async def delete_record(short_url: str, session: AsyncSession = Depends(get_async_session)):
#     """ Удаляет запись. Первый запрос на удаление меняет статус, второй - удаляет объект из БД """
#     query = select(ShortUrlSchema).where(ShortUrlSchema.short_url == short_url)
#     execute = await session.execute(query)
#     result = execute.scalars().all()
#     if not result:
#         logger.info(f'[delete_record()] 404: {short_url}')
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Record does not exist',
#         )
#
#     if result[0].active:
#         statement: Update | Delete = update(ShortUrlSchema).where(ShortUrlSchema.short_url == short_url).values({
#             'active': False,
#         })
#         res: ShortUrlSchema | Response = result[0]
#     else:
#         statement = delete(ShortUrlSchema).where(ShortUrlSchema.short_url == short_url)
#         res = Response(status_code=status.HTTP_204_NO_CONTENT)
#
#     await session.execute(statement)
#     await session.commit()
#     return res
#
#
# @router.get('/ping/')
# async def check_db_connect(session: AsyncSession = Depends(get_async_session)):
#     """ Проверяет статус подключения к БД. Обратить внимание на закрывающийся слэш в эндпоинте и строке запроса! """
#     query = select(ShortUrlSchema).limit(1)
#
#     try:
#         await session.execute(query)
#         logger.info('DB connect: success')
#         return {'success': True, 'detail': None}
#     except exceptions.InvalidPasswordError as exc:
#         logger.info(f'DB connect: failure. Exception: {exc}')
#         return {'success': False, 'detail': exc}
#     except exceptions.InvalidCatalogNameError as exc:
#         logger.info(f'DB connect: failure. Exception: {exc}')
#         return {'success': False, 'detail': exc}
#     except (socket.gaierror, OSError):
#         logger.info('DB connect: failure. Exception: Invalid db host or port')
#         return {'success': False, 'detail': 'Invalid db host or port'}
#     except asyncio.exceptions.TimeoutError:
#         logger.info('DB connect: failure. Exception: TimeoutError')
#         return {'success': False, 'detail': 'TimeoutError'}
#     except Exception as exc:
#         logger.info(f'DB connect: failure. Unexpected Error: {exc}')
#         return {'success': False, 'detail': exc}
