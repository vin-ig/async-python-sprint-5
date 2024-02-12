import uuid

from fastapi_users import FastAPIUsers

from .auth.auth import auth_backend
from .auth.database import User
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from fastapi_users import fastapi_users

from .app.main import router as api_router
from .auth.manager import get_user_manager
from .auth.schemas import UserRead, UserCreate
from .core.config import app_settings
# from .services.middleware import check_allowed_ip

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    # dependencies=[Depends(check_allowed_ip)]
)
app.include_router(api_router)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
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
