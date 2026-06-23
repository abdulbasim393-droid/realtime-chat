from fastapi import FastAPI
from app.schemas import UserCreate, UserResponse
from app.database import Base, engine


app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Real Time Chat Backend Running"
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id
    }


@app.get("/messages")
def get_messages(
    page: int = 1,
    limit: int = 20
):
    return {
        "page": page,
        "limit": limit
    }


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return user




