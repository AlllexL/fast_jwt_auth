from datetime import timedelta

from users.schemas import UserSchemas
from auth import utils as utils_auth
from core.config import settings

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_time_delta: timedelta | None = None,
):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return utils_auth.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_time_delta=expire_time_delta,
    )


def create_access_token(user: UserSchemas) -> str:
    jwt_payload = {
        "sub": user.username,  # vmesto id
        "username": user.username,
        "email": user.email,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: UserSchemas) -> str:
    jwt_payload = {"sub": user.username}  # vmesto id
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_time_delta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
