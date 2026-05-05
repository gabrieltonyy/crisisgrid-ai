"""HTTP error helpers that avoid exposing backend internals."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


DATABASE_UNAVAILABLE_DETAIL = (
    "Database unavailable. Ensure PostgreSQL is running and the local database "
    "has been initialized."
)


def is_database_unavailable_error(exc: BaseException) -> bool:
    """Return True for SQLAlchemy/database connectivity failures."""

    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, SQLAlchemyError):
            return True
        current = current.__cause__ or current.__context__

    message = str(exc).lower()
    return any(
        marker in message
        for marker in [
            "psycopg2.operationalerror",
            "connection refused",
            "could not connect to server",
            "database connection failed",
        ]
    )


def database_unavailable_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=DATABASE_UNAVAILABLE_DETAIL,
    )
