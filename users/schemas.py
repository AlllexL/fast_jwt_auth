from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchemas(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str | bytes
    email: str | None = None
    active: bool = True
