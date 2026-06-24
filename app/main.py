from fastapi import FastAPI, Depends, HTTPException
from app.schemas import UserCreate, UserResponse, UserLogin
from app.database import Base, engine, get_db
from sqlalchemy.orm import Session
from app.models import User
from app.security import hash_password, verify_password




app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Real Time Chat Backend Running"
    }



@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        user_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return {
        "message": "Login successful"
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




@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    return {"message": "Database dependency works"}

@app.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user



@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user