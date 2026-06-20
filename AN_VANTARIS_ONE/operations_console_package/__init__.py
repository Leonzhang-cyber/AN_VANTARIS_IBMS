"""Read-only Operations Console Package foundation."""

from .enums import CONTRACT_VERSION
from .projection import build_operations_console_package

__all__ = ["CONTRACT_VERSION", "build_operations_console_package"]
