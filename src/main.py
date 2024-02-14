import asyncio
import socket
from asyncio import exceptions

from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .app.main import router as api_router
from .auth.auth import auth_backend, fastapi_users
from .auth.schemas import UserRead, UserCreate
from .core.config import app_settings, logger
from .db.db import get_async_session
from .models import User

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(api_router)


@app.get('/ping/')
async def check_db_connect(session: AsyncSession = Depends(get_async_session)):
    """ Проверяет статус подключения к БД. Обратить внимание на закрывающийся слэш в эндпоинте и строке запроса! """
    query = select(User).limit(1)

    try:
        await session.execute(query)
        logger.info('DB connect: success')
        return {'success': True, 'detail': None}
    except exceptions.InvalidPasswordError as exc:
        logger.info(f'DB connect: failure. Exception: {exc}')
        return {'success': False, 'detail': exc}
    except exceptions.InvalidCatalogNameError as exc:
        logger.info(f'DB connect: failure. Exception: {exc}')
        return {'success': False, 'detail': exc}
    except (socket.gaierror, OSError):
        logger.info('DB connect: failure. Exception: Invalid db host or port')
        return {'success': False, 'detail': 'Invalid db host or port'}
    except asyncio.exceptions.TimeoutError:
        logger.info('DB connect: failure. Exception: TimeoutError')
        return {'success': False, 'detail': 'TimeoutError'}
    except Exception as exc:
        logger.info(f'DB connect: failure. Unexpected Error: {exc}')
        return {'success': False, 'detail': exc}
