from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for simplicity and portability in this demo, but easy to switch to Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def check_connection():
    url_present = bool(os.getenv("DATABASE_URL"))
    print("ENV_LOADED" if url_present else "NO_DB_URL")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    create_db_and_tables()
    print("CONNECTED")
    print("TABLES_CREATED")

if __name__ == "__main__":
    check_connection()
