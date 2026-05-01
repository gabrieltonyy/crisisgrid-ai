"""
Database Initialization Script

Creates all database tables and optionally seeds initial data.
"""

import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine, get_db_info
from app.models.base import BaseModel
import app.models  # noqa: F401 - register model metadata before create_all/drop_all

logger = logging.getLogger(__name__)


def create_tables() -> bool:
    """
    Create all database tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        BaseModel.metadata.create_all(bind=engine)
        
        logger.info("✓ Database tables created successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to create database tables: {e}")
        return False


def drop_tables() -> bool:
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("Dropping all database tables...")
        
        BaseModel.metadata.drop_all(bind=engine)
        
        logger.info("✓ Database tables dropped successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to drop database tables: {e}")
        return False


def reset_database() -> bool:
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.warning("Resetting database...")
    
    if not drop_tables():
        return False
    
    if not create_tables():
        return False
    
    logger.info("✓ Database reset complete")
    return True


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("✓ Database connection successful")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def get_table_info() -> dict:
    """
    Get information about existing tables.
    
    Returns:
        dict: Table information
    """
    try:
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = {}
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            table_info[table_name] = {
                "columns": [col["name"] for col in columns],
                "column_count": len(columns)
            }
        
        return {
            "table_count": len(tables),
            "tables": table_info
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to get table info: {e}")
        return {}


def init_database(reset: bool = False) -> bool:
    """
    Initialize database.
    
    Args:
        reset: If True, drop and recreate all tables (WARNING: deletes data)
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 60)
    
    # Check connection
    if not check_database_connection():
        logger.error("Cannot proceed without database connection")
        return False
    
    # Show database info
    db_info = get_db_info()
    logger.info(f"Database: {db_info.get('database', 'Unknown')}")
    logger.info(f"Host: {db_info.get('host', 'Unknown')}")
    logger.info(f"Port: {db_info.get('port', 'Unknown')}")
    
    # Reset or create tables
    if reset:
        logger.warning("RESET MODE: All existing data will be deleted!")
        if not reset_database():
            return False
    else:
        if not create_tables():
            return False
    
    # Show table info
    table_info = get_table_info()
    logger.info(f"Tables created: {table_info.get('table_count', 0)}")
    
    if table_info.get('tables'):
        logger.info("\nTable Details:")
        for table_name, info in table_info['tables'].items():
            logger.info(f"  - {table_name}: {info['column_count']} columns")
    
    logger.info("=" * 60)
    logger.info("✓ DATABASE INITIALIZATION COMPLETE")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize database
    import sys
    reset = "--reset" in sys.argv
    
    if reset:
        logger.warning("WARNING: --reset flag detected. All data will be deleted!")
        response = input("Are you sure you want to reset the database? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Database reset cancelled")
            sys.exit(0)
    
    success = init_database(reset=reset)
    sys.exit(0 if success else 1)

# Made with Bob
