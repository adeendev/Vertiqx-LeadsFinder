from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for simplicity and portability in this demo, but easy to switch to Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
