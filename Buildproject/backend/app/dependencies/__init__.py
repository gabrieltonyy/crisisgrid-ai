"""
Dependencies package for CrisisGrid AI.
Contains FastAPI dependency functions for authentication and other cross-cutting concerns.
"""

from app.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    require_role,
    require_authority,
    require_admin,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_role",
    "require_authority",
    "require_admin",
]

# Made with Bob