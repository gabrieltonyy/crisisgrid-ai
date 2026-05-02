"""Timestamp utilities for timezone-aware datetime handling."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC timestamp with timezone awareness."""
    return datetime.now(timezone.utc)


def format_iso8601(dt: datetime) -> str:
    """Format datetime as ISO 8601 string."""
    return dt.isoformat()

# Made with Bob
