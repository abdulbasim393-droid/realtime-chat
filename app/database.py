from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
DATABASE_URL = "postgresql://postgres:password@localhost/chatdb"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()