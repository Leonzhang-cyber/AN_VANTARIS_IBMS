"""API / Frontend readiness contract foundation."""

from .enums import CONTRACT_VERSION
from .models import build_api_frontend_readiness_contract

__all__ = ["CONTRACT_VERSION", "build_api_frontend_readiness_contract"]
