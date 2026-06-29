from fastapi import FastAPI, Depends, HTTPException
from app.schemas import(
    UserCreate, 
    UserResponse, 
    Token, 
    ConversationCreate, 
    ConversationResponse,
    MessageCreate,
    MessageResponse
    )
from app.database import Base, engine, get_db, SessionLocal
from sqlalchemy.orm import Session
from app.models import User, Conversation, Message
from app.security import hash_password, verify_password, create_access_token
from app.security import (
    oauth2_scheme,
    verify_access_token,
    
    )

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket_manager import manager



app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Real Time Chat Backend Running"
    }







@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):
    email = verify_access_token(token)

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user

#To get own details
@app.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user)
    ):
    return current_user




@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
    ):
    db_conversation = Conversation(
        name=conversation.name
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


@app.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse
)
def create_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    new_message = Message(
        content=message.content
    )

    new_message.user = current_user
    new_message.conversation = conversation

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message



@app.get(
    "/conversations",
    response_model=list[ConversationResponse]
)
def get_conversations(
    db: Session = Depends(get_db)
):
    return db.query(Conversation).all()



@app.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    return messages



@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int
    ):
    await manager.connect(
        conversation_id,
        websocket
        )

    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_json()
            token = data["token"]
            content = data["content"]

            email = verify_access_token(token)
            if not email:
                await websocket.close()
                break

            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            if not user:
                await websocket.close()
                break

            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
                )

            if not conversation:
                await websocket.close()
                break

            new_message = Message(
                 content=content
                )

            new_message.user = user
            new_message.conversation = conversation

            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            await manager.broadcast(
                conversation_id,
                {
                    "id": new_message.id,
                    "content": new_message.content,
                    "username": user.username,
                    "created_at": new_message.created_at.isoformat()
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(
            conversation_id,
            websocket
        )

    finally:
        db.close()