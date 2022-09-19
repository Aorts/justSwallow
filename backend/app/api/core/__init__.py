from . import deps
from . import jwt_util

jwt_handler = None


def get_jwt_handler():
    global jwt_handler

    if not jwt_handler:
        from app.config import settings

        jwt_handler = jwt_util.JWTUtil(
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    return jwt_handler
