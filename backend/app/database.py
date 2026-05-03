"""
Database configuration and session management.
Production-ready (PostgreSQL only).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


# Create PostgreSQL engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False  # set True only for debugging
)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for models
Base = declarative_base()


# Dependency (used in FastAPI routes)
def get_db():
    """Provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()