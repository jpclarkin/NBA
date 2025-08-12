"""
Database session management for NBA data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from nba.config import get_settings
from .models import Base


def get_session_factory() -> sessionmaker:
    """Get SQLAlchemy session factory."""
    settings = get_settings()
    
    # Configure engine with appropriate settings for SQLite
    if "sqlite" in settings.database_url:
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(settings.database_url, echo=False)
    
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_all_tables() -> None:
    """Create all database tables."""
    settings = get_settings()
    
    if "sqlite" in settings.database_url:
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(settings.database_url, echo=False)
    
    Base.metadata.create_all(bind=engine)
