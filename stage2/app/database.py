from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# If no DATABASE_URL, construct from individual env vars (for local development)
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "country_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "country_db")
    
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD environment variable must be set for local development")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create database engine

engine = create_engine(DATABASE_URL)


# SessionLocal: Factory for database sessions
SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)

# Base class for all models
Base = declarative_base()


# Dependency to inject database session
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
