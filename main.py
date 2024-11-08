import uvicorn

from fastapi import FastAPI, APIRouter
from pydantic import EmailStr, BaseModel

from item_views import router as items_router

app = FastAPI()
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
