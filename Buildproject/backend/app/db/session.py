"""
Database session management for CrisisGrid AI.
Handles PostgreSQL connection and session lifecycle.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
    echo=settings.APP_DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection successful, False otherwise.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLAlchemy models.
    
    Note: In production, use Alembic migrations instead.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {str(e)}")
        raise


def get_db_info() -> dict:
    """
    Get database connection information (without sensitive data).
    Returns basic connection status and metadata.
    """
    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            # Get database name
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            
            return {
                "connected": True,
                "database": db_name,
                "version": version.split(",")[0],  # First part of version string
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {
            "connected": False,
            "error": str(e)
        }

# Made with Bob
