from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Get absolute path to database file based on this file's location
DB_DIR = Path(__file__).parent
DATABASE_PATH = DB_DIR / "queue.db"

# Create SQLite engine for queue database with absolute path
QUEUE_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    QUEUE_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 