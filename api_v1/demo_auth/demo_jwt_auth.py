from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import BaseModel


from .helpers import (
    create_refresh_token,
    create_access_token,
)

from users.schemas import UserSchemas
from fastapi.security import (
    HTTPBearer,
)
from auth import utils as utils_auth
from .validation import (
    get_current_auth_user,
    get_current_token_payload_user,
    get_current_auth_user_for_refresh_token,
    REFRESH_TOKEN_TYPE,
    UserGetterFromToken,
    get_auth_user_from_token_of_type,
)
from .fake_db import users_db

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/jwt", tags=["JWT"], dependencies=[Depends(http_bearer)])


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


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


def get_current_active_auth_user(user: UserSchemas = Depends(get_current_auth_user)):
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchemas = Depends(validate_auth_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_user_refresh_token(
    # user: UserSchemas = Depends(get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)),
    user: UserSchemas = Depends(get_current_auth_user_for_refresh_token),
):
    access_token = create_access_token(user)
    return TokenInfo(access_token=access_token)


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload_user),
    user: UserSchemas = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")

    return {"user": user.username, "email": user.email, "logged_at": iat}
