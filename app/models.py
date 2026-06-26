from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String)
    email = Column(String)
    password = Column(String)

    messages = relationship(
        "Message",
        back_populates="user"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    messages = relationship(
        "Message",
        back_populates="conversation"
    )



class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    content = Column(String)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id")
    )

    user = relationship(
        "User",
        back_populates="messages"
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )