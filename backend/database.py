from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# This creates a local file named 'vendorbridge.db' in your backend folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./vendorbridge.db"

# check_same_thread=False is strictly required for SQLite + FastAPI to work together
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency injection to safely open and close DB sessions per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()