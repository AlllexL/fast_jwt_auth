import secrets
import uuid
from typing import Annotated, Any
from time import time

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasicCredentials, HTTPBasic

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_credential(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return {
        "message": "hi",
        "username": credentials.username,
        "password": credentials.password,
    }


username_to_password = {"admin": "admin", "john": "super"}

static_auth_token_to_username = {
    "df6803d89a8f39fc006f7eed2f7bde": "admin",
    "59ec643dd9597839294ca38842352f2fce": "john",
}


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:

    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW_Authenticate": "Basic"},
    )

    correct_password = username_to_password.get(credentials.username)
    if correct_password is None:
        raise unauth_exc

    if credentials.username not in username_to_password:
        raise unauth_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"), correct_password.encode("utf-8")
    ):
        raise unauth_exc
    return credentials.username


def get_username_by_static_token(
    static_token: str = Header(alias="x-auth-token"),
) -> str:
    # if static_token not in static_auth_token_to_username:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail='invalid token'
    #     )
    # return static_auth_token_to_username[static_token]
    #### new version ###
    if username := static_auth_token_to_username.get(static_token):
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
    )


@router.get("/basic-auth-username/")
def demo_basic_username(auth_username: str = Depends(get_auth_user_username)):
    return {
        "message": f"hi, {auth_username}",
        "username": auth_username,
    }


@router.get("/some-http-header-auth/")
def some_http_header_auth(username: str = Depends(get_username_by_static_token)):
    return {
        "message": f"hi, {username}",
        "username": username,
    }


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def get_session_data(session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY)):
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated"
        )
    return COOKIES[session_id]


def generate_session_id() -> str:
    au = uuid.uuid4().hex
    print(au)
    return au


@router.post("/login-cookie/")
def demo_auth_login_set_cookies(
    response: Response,
    # auth_username: str = Depends(get_auth_user_username),
    auth_username: str = Depends(get_username_by_static_token),
):
    session_id = generate_session_id()
    print(f"{session_id=}")
    COOKIES[session_id] = {"username": auth_username, "login_at": int(time())}
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok!"}


@router.get("/check-cookie")
def demo_auth_check_cookies(
    user_session_data: dict = Depends(get_session_data),
):
    username = user_session_data["username"]

    return {"message": f"Hello, {username}", **user_session_data}


@router.get("/logout-cookie")
def demo_auth_logout_cookies(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    response.delete_cookie(session_id)
    username = user_session_data["username"]

    return {"message": f"Bye, {username}"}
