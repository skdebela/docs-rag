from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from .models import Base
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chatrag.db"))
CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma_db"))
os.makedirs(CHROMA_PATH, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
