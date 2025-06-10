from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from a .env file

from sqlmodel import create_engine, Session, SQLModel
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./crm.db")
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)