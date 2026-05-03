"""
Database Initialization Script

Creates all database tables and verifies compatibility columns required by
the authentication system.

Run from Buildproject/backend:

    python -m app.db.init_db

Optional destructive reset:

    python -m app.db.init_db --reset
"""

import logging
import sys

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine, get_db_info
from app.models.base import BaseModel

# IMPORTANT:
# Import all models so SQLAlchemy registers their metadata before create_all().
# Without this, tables like users/reports may not be created.
import app.models  # noqa: F401

from app.services.auth_service import hash_password

logger = logging.getLogger(__name__)


def create_tables() -> bool:
    """
    Create all database tables and verify auth compatibility columns.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Creating database tables...")

        # Create all tables registered under BaseModel metadata.
        BaseModel.metadata.create_all(bind=engine)

        # Ensure auth-related columns exist for older databases.
        if not ensure_auth_columns():
            logger.warning(
                "Database tables were created, but auth column verification failed. "
                "Login may fail until auth columns are fixed."
            )
            return False

        logger.info("✓ Database tables created/verified successfully")
        return True

    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to create database tables: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error while creating database tables: {e}", exc_info=True)
        return False


def ensure_auth_columns() -> bool:
    """
    Add auth columns to existing hackathon databases created before auth landed.

    This is a small compatibility bridge until formal Alembic migrations are added.

    Required columns:
      - users.hashed_password
      - users.is_active
      - users.email_verified

    Returns:
        bool: True if successful, False otherwise
    """
    previous_echo = getattr(engine, "echo", False)

    try:
        engine.echo = False

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "users" not in tables:
            logger.warning(
                "users table does not exist yet. Skipping auth column verification. "
                "Run create_tables() after all models are imported."
            )
            return False

        default_hash = hash_password("Password123!")

        with engine.begin() as conn:
            # hashed_password is required by auth_service/login.
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)"
                )
            )

            # Existing users from older seed data need a password hash.
            conn.execute(
                text(
                    "UPDATE users "
                    "SET hashed_password = :password_hash "
                    "WHERE hashed_password IS NULL OR hashed_password = ''"
                ),
                {"password_hash": default_hash},
            )

            # Only set NOT NULL after backfilling values.
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ALTER COLUMN hashed_password SET NOT NULL"
                )
            )

            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE"
                )
            )

            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )

        logger.info("✓ Auth columns verified")
        return True

    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to verify auth columns: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error while verifying auth columns: {e}", exc_info=True)
        return False
    finally:
        engine.echo = previous_echo


def drop_tables() -> bool:
    """
    Drop all database tables.

    WARNING: This will delete all data.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("Dropping all database tables...")

        BaseModel.metadata.drop_all(bind=engine)

        logger.info("✓ Database tables dropped successfully")
        return True

    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to drop database tables: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error while dropping database tables: {e}", exc_info=True)
        return False


def reset_database() -> bool:
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data.

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
        logger.error(f"✗ Database connection failed: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected database connection error: {e}", exc_info=True)
        return False


def get_table_info() -> dict:
    """
    Get information about existing tables.

    Returns:
        dict: Table information
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        table_info = {}

        for table_name in tables:
            columns = inspector.get_columns(table_name)
            table_info[table_name] = {
                "columns": [col["name"] for col in columns],
                "column_count": len(columns),
            }

        return {
            "table_count": len(tables),
            "tables": table_info,
        }

    except SQLAlchemyError as e:
        logger.error(f"Failed to get table info: {e}", exc_info=True)
        return {}
    except Exception as e:
        logger.error(f"Unexpected error getting table info: {e}", exc_info=True)
        return {}


def init_database(reset: bool = False) -> bool:
    """
    Initialize database.

    Args:
        reset: If True, drop and recreate all tables.

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
    logger.info(f"Tables found: {table_info.get('table_count', 0)}")

    if table_info.get("tables"):
        logger.info("\nTable Details:")
        for table_name, info in table_info["tables"].items():
            logger.info(f"  - {table_name}: {info['column_count']} columns")

    logger.info("=" * 60)
    logger.info("✓ DATABASE INITIALIZATION COMPLETE")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

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