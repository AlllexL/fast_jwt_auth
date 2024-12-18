import datetime

from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import BaseModel

from users.schemas import UserSchemas
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from auth import utils as utils_auth

router = APIRouter(prefix="/jwt", tags=["JWT"])


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


# http_bearer = HTTPBearer()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/login/")

john = UserSchemas(
    username="john",
    password=utils_auth.hash_password("qwerty"),
    email="john@example.com",
)

sam = UserSchemas(
    username="sam",
    password=utils_auth.hash_password("secret"),
)

users_db: dict[str, UserSchemas] = {john.username: john, sam.username: sam}


def validate_auth_user(username: str = Form(), password: str = Form()):
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
    )

    if not (user := users_db.get(username)):
        raise unauth_exc
    if not utils_auth.validate_password(
        password=password, hashed_password=user.password
    ):
        raise unauth_exc
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user inactive"
        )
    return user


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


def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload_user),
) -> UserSchemas:
    username: str | None = payload.get("sub")
    if user := users_db.get(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid"
    )


def get_current_active_auth_user(user: UserSchemas = Depends(get_current_auth_user)):
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchemas = Depends(validate_auth_user)):
    jwt_payload = {
        "sub": user.username,  # vmesto id
        "username": user.username,
        "email": user.email,
    }
    token = utils_auth.encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="Bearer")


@router.get("/users/me")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload_user),
    user: UserSchemas = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")

    return {"user": user.username, "email": user.email, "logged_at": iat}
