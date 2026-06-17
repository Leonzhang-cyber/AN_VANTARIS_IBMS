# src/common/utils/permission_util.py
"""Authorization helpers — JWT authentication remains in jwt_util.jwt_required."""

from functools import wraps
from typing import Any, Iterable, List, Optional, Sequence, Union

from flask import g

from src.common.models.response import Result

PermissionCode = str
PermissionInput = Union[PermissionCode, Sequence[PermissionCode]]


def _coerce_permission_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item is not None and str(item).strip()]
    return []


def _permissions_from_payload(payload: dict) -> List[str]:
    if not payload:
        return []
    for key in ('perms', 'permission_codes', 'permissions'):
        perms = _coerce_permission_list(payload.get(key))
        if perms:
            return perms
    return []


def _permissions_from_g() -> List[str]:
    principal = getattr(g, 'current_principal', None)
    if isinstance(principal, dict):
        perms = _coerce_permission_list(principal.get('permissions'))
        if perms:
            return perms

    perms = _coerce_permission_list(getattr(g, 'user_permissions', None))
    if perms:
        return perms

    payload = getattr(g, 'jwt_payload', None)
    if isinstance(payload, dict):
        return _permissions_from_payload(payload)

    return []


def get_current_principal() -> dict:
    """Return current authenticated principal from Flask g (requires prior jwt_required)."""
    principal = getattr(g, 'current_principal', None)
    if isinstance(principal, dict):
        return {
            'did': principal.get('did') or getattr(g, 'current_did', None),
            'permissions': _coerce_permission_list(principal.get('permissions')) or _permissions_from_g(),
        }

    return {
        'did': getattr(g, 'current_did', None),
        'permissions': _permissions_from_g(),
    }


def get_current_permissions() -> List[str]:
    """Effective permission codes for the current request."""
    return _permissions_from_g()


def _permission_matches(required: PermissionCode, granted: PermissionCode) -> bool:
    if granted == '*':
        return True
    if granted == required:
        return True
    if granted.endswith(':*'):
        prefix = granted[:-2]
        return required == prefix or required.startswith(f'{prefix}:')
    return False


def has_permission(permission_code: PermissionCode) -> bool:
    if not permission_code:
        return False
    for granted in get_current_permissions():
        if _permission_matches(permission_code, granted):
            return True
    return False


def has_any_permission(permission_codes: Iterable[PermissionCode]) -> bool:
    codes = [code for code in permission_codes if code]
    if not codes:
        return False
    return any(has_permission(code) for code in codes)


def safe_permission_denied_response(permission_code_or_list: PermissionInput):
    """403 response using existing Result.error envelope."""
    if isinstance(permission_code_or_list, (list, tuple, set)):
        codes = [str(code) for code in permission_code_or_list]
        message = f"Permission denied: requires one of {codes}"
    else:
        message = f"Permission denied: requires [{permission_code_or_list}]"
    return Result.error(message=message, code=403)


def require_permission(permission_code: PermissionCode):
    """Decorator — run after @jwt_required; returns 403 when permission missing."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_permission(permission_code):
                return safe_permission_denied_response(permission_code)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_any_permission(permission_codes: Sequence[PermissionCode]):
    """Decorator — run after @jwt_required; returns 403 when none of the codes match."""

    codes = tuple(permission_codes)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_any_permission(codes):
                return safe_permission_denied_response(codes)
            return func(*args, **kwargs)

        return wrapper

    return decorator
