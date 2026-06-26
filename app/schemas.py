from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ConversationCreate(BaseModel):
    name: str

class ConversationResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True




class MessageCreate(BaseModel):
    content: str



class MessageResponse(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = True