"""Local DB smoke helpers for read-only system routes (menus, permissions, versions).

Activated only when IBMS_LOCAL_SMOKE=true. Does not change JWT or auth behavior.
"""
import os

from flask import jsonify

from src.common.models.response import Result

DB_UNAVAILABLE_MESSAGE = "Database unavailable during local smoke"
DB_UNAVAILABLE_CODE = "DB_UNAVAILABLE"

LOCAL_SMOKE_MENUS = [
    {
        "id": 1,
        "parent_id": 0,
        "menu_path": "/smoke/dashboard",
        "menu_title": "Smoke Dashboard",
        "menu_icon": "dashboard",
        "menu_type": "menu",
        "has_children": False,
        "redirect_path": None,
        "sort_order": 1,
        "is_visible": True,
        "children": [],
    }
]

LOCAL_SMOKE_PERMISSIONS = [
    {
        "id": "smoke-perm-001",
        "perm_code": "system:smoke:read",
        "description": "Local smoke read permission",
        "extra": None,
    }
]

LOCAL_SMOKE_VERSIONS = [
    {
        "id": 1,
        "version_code": "smoke-v1",
        "version_name": "Local Smoke Version",
        "description": "Stable fixture for IBMS local DB smoke",
        "icon": "smoke",
        "sort_order": 0,
        "is_active": True,
        "is_default": True,
    }
]


def is_local_smoke_enabled() -> bool:
    value = os.getenv("IBMS_LOCAL_SMOKE", "")
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def is_db_connection_error(exc: Exception) -> bool:
    try:
        from sqlalchemy.exc import OperationalError
    except ImportError:
        OperationalError = ()  # type: ignore

    if isinstance(exc, OperationalError):
        return True

    message = str(exc).lower()
    markers = (
        "connection refused",
        "can't connect",
        "cannot connect",
        "lost connection",
        "server has gone away",
        "access denied for user",
        "unknown database",
        "name or service not known",
        "timed out",
    )
    return any(marker in message for marker in markers)


def db_unavailable_response():
    return jsonify(
        {
            "success": False,
            "error": {
                "code": DB_UNAVAILABLE_CODE,
                "message": DB_UNAVAILABLE_MESSAGE,
            },
        }
    ), 500


def handle_db_smoke_error(exc: Exception):
    if is_db_connection_error(exc):
        return db_unavailable_response()
    return Result.error(code=500, message=DB_UNAVAILABLE_MESSAGE)


def local_smoke_menus_response():
    return Result.success(LOCAL_SMOKE_MENUS)


def local_smoke_permissions_response():
    return Result.success(LOCAL_SMOKE_PERMISSIONS)


def local_smoke_versions_response():
    return Result.success(LOCAL_SMOKE_VERSIONS)
