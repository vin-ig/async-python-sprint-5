from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, AuthenticationBackend, JWTStrategy

from src.auth.manager import get_user_manager
from src.core.config import app_settings
from src.models import User

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = app_settings.bearer_secret.get_secret_value()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=5 * 24 * 3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
current_user = fastapi_users.current_user()
