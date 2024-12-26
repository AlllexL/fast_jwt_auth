from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status

from api_v1.demo_auth.fake_db import users_db
from api_v1.demo_auth.helpers import (
    TOKEN_TYPE_FIELD,
    REFRESH_TOKEN_TYPE,
    ACCESS_TOKEN_TYPE,
)
from auth import utils as utils_auth
from users.schemas import UserSchemas

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/login/")


def get_current_token_payload_user(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_schema),
) -> UserSchemas:
    # token = credentials.credentials

    try:
        payload = utils_auth.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token error: {e}"
        )
    print(payload)
    return payload


def validate_token_type(
    payload: dict,
    token_type: str,
):
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"token type {current_token_type!r} invalid  - expected {token_type!r}",
    )


def get_auth_user_from_token_of_type(token_type: str):
    def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload_user),
    ) -> UserSchemas:
        validate_token_type(payload, token_type)
        return get_user_by_token_sub(payload)

    return get_auth_user_from_token


def get_user_by_token_sub(payload: dict) -> UserSchemas:
    username: str | None = payload.get("sub")
    if user := users_db.get(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid"
    )


#
# def get_current_auth_user(
#     payload: dict = Depends(get_current_token_payload_user),
# ) -> UserSchemas:
#     validate_token_type(payload, ACCESS_TOKEN_TYPE)
#     return get_user_by_token_sub(payload)

get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)


#
# def get_current_auth_user_for_refresh_token(
#     payload: dict = Depends(get_current_token_payload_user),
# ) -> UserSchemas:
#     validate_token_type(payload, REFRESH_TOKEN_TYPE)
#     return get_user_by_token_sub(payload)


class UserGetterFromToken:
    def __init__(self, token_type):
        self.token_type = token_type

    def __call__(self, payload: dict = Depends(get_current_token_payload_user)):
        validate_token_type(payload, self.token_type)
        return get_user_by_token_sub(payload)


get_current_auth_user_for_refresh_token = UserGetterFromToken(REFRESH_TOKEN_TYPE)
