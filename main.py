from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI, APIRouter
from pydantic import EmailStr, BaseModel
from api_v1 import router as router_v1
from core.config import settings
from item_views import router as items_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router_v1, prefix=settings.api_v1_prefix)
app.include_router(items_router, tags=["Items"])


class CreateUser(BaseModel):
    email: EmailStr


@app.get("/")
def hello_index():
    return {"message": "Hello index!"}


@app.post("/users")
def create_user(user: CreateUser):
    return {"message": "success", "email": user.email}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
