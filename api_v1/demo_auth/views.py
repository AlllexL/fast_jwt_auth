import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):

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


@router.get("/basic-auth-username/")
def demo_basic_username(auth_username: str = Depends(get_auth_user_username)):
    return {
        "message": f"hi, {auth_username}",
        "username": auth_username,
    }
