import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# Store the database file next to the executable (or in the project root during dev)
# sys._MEIPASS is set by PyInstaller at runtime; fall back to cwd for dev
import sys
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle — put the db beside the .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as normal Python — put the db in the project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(BASE_DIR, "ocularguard.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # Required for SQLite + multithreading
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    print(f"Initialising database at: {DB_PATH}")
    Base.metadata.create_all(bind=engine)
    print("Tables ready.")


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
