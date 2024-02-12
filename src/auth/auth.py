from fastapi_users.authentication import BearerTransport, AuthenticationBackend, JWTStrategy

from src.core.config import app_settings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = app_settings.bearer_secret.get_secret_value()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)