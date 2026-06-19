"""UEDGE service layer (read-only setup and diagnostics skeleton)."""

from __future__ import annotations

from typing import Any, Dict

from src.uedge.uedge_provider import (
    get_customer_setup,
    get_diagnostics_panels,
    get_engineer_diagnostics,
    get_setup_steps,
    get_uedge_health,
    get_uedge_summary,
)


class UedgeService:
    MODULE_ID = "uedge"
    MODULE_NAME = "UEDGE Setup & Diagnostics"
    PROVIDER = "local-uedge-provider"
    RUNTIME_MODE = "local-skeleton"

    def get_uedge_health(self) -> Dict[str, Any]:
        return get_uedge_health()

    def get_customer_setup(self) -> Dict[str, Any]:
        return get_customer_setup()

    def get_setup_steps(self) -> Dict[str, Any]:
        rows = get_setup_steps()
        return {
            "items": rows,
            "total": len(rows),
            "setupMode": "local-skeleton-setup-steps",
            "runtimeLinked": False,
            "readOnly": True,
            "controlActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_engineer_diagnostics(self) -> Dict[str, Any]:
        return get_engineer_diagnostics()

    def get_diagnostics_panels(self) -> Dict[str, Any]:
        rows = get_diagnostics_panels()
        return {
            "items": rows,
            "total": len(rows),
            "diagnosticsMode": "local-skeleton-diagnostics-panels",
            "runtimeLinked": False,
            "readOnly": True,
            "controlActionsEnabled": False,
            "certified": False,
            "iec62443Certified": False,
        }

    def get_uedge_summary(self) -> Dict[str, Any]:
        return get_uedge_summary()

