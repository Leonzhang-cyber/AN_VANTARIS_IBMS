"""UHMI UConsole workspace read-only provider.

The provider exposes local projection data for the UHMI workspace UI/API
skeleton. It does not connect to devices, write databases, execute commands,
activate runtime paths, or bypass CODE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


MENU_ITEMS: list[dict[str, str]] = [
    {"key": "HMI_OVERVIEW", "label": "HMI Overview", "route": "/one/uhmi/overview"},
    {"key": "SYSTEM_HMI", "label": "System HMI", "route": "/one/uhmi/system"},
    {"key": "DEVICE_HMI", "label": "Device HMI", "route": "/one/uhmi/device"},
    {"key": "ALARM_EVENT_HMI", "label": "Alarm & Event HMI", "route": "/one/uhmi/alarms-events"},
    {"key": "EDGE_LINK_DIAGNOSTICS", "label": "EDGE / LINK Diagnostics", "route": "/one/uhmi/edge-link-diagnostics"},
    {"key": "EVIDENCE_REPORTS", "label": "Evidence & Reports", "route": "/one/uhmi/evidence-reports"},
]

FORBIDDEN_DIRECT_PATHS = [
    "UHMI -> Device",
    "UHMI -> DB write",
    "UHMI -> EDGE command",
    "UHMI -> LINK command",
    "UHMI -> NEXUS AI execution",
    "UHMI -> bypass CODE",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _guardrails() -> dict[str, Any]:
    return {
        "readOnly": True,
        "runtimeActivation": False,
        "productionActivation": False,
        "controlActionsEnabled": False,
        "directDeviceControl": False,
        "directDatabaseWrite": False,
        "edgeCommandEnabled": False,
        "linkCommandEnabled": False,
        "nexusAiExecution": False,
        "bypassCode": False,
        "dbMigration": False,
        "installOrRollback": False,
        "futureControlledActionExecuted": False,
    }


def _section(key: str, label: str, route: str, purpose: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "platform": "VANTARIS_ONE",
        "capability": "UHMI",
        "definition": "UHMI = Unified Human-Machine Interface",
        "placement": "UConsole / UHMI Workspace",
        "releaseScope": "READ_ONLY_UI_API_SKELETON",
        "sectionKey": key,
        "sectionLabel": label,
        "route": route,
        "method": "GET",
        "purpose": purpose,
        "dataFlow": "Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI",
        "futureControlledActionPath": "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device",
        "futureControlledActionStatus": "NOT EXECUTED in R2A",
        "forbiddenDirectPaths": FORBIDDEN_DIRECT_PATHS,
        "l3WorkspaceInsidePage": True,
        "lastUpdated": _now_iso(),
        "rows": rows,
    }
    payload.update(_guardrails())
    return payload


def get_menu_ia() -> dict[str, Any]:
    data: dict[str, Any] = {
        "platform": "VANTARIS_ONE",
        "capability": "UHMI",
        "placement": "UConsole / UHMI Workspace",
        "l1": "UConsole",
        "l2": "UHMI Workspace",
        "l3Policy": "L3 workspace views render inside the UHMI page, not the sidebar.",
        "menuItems": MENU_ITEMS,
        "productionLabelPolicy": "Production UI must not use Mock/Demo/Pilot/Coming soon labels.",
    }
    data.update(_guardrails())
    return data


def get_health() -> dict[str, Any]:
    data: dict[str, Any] = {
        "status": "PASS",
        "moduleId": "uhmi",
        "moduleName": "Unified Human-Machine Interface",
        "placement": "UConsole / UHMI Workspace",
        "readOnlyFoundation": True,
        "uiSkeletonReady": True,
        "apiSkeletonReady": True,
        "menuItemCount": len(MENU_ITEMS),
        "lastUpdated": _now_iso(),
    }
    data.update(_guardrails())
    return data


def list_sections() -> list[dict[str, Any]]:
    return [
        get_section(item["key"]) for item in MENU_ITEMS
    ]


def get_section(section_key: str) -> dict[str, Any]:
    normalized = section_key.strip().upper().replace("-", "_")
    item = next((entry for entry in MENU_ITEMS if entry["key"] == normalized), MENU_ITEMS[0])
    rows_by_key: dict[str, list[dict[str, Any]]] = {
        "HMI_OVERVIEW": [
            {"name": "Workspace status", "state": "Ready", "source": "CODE projection", "actionEnabled": False},
            {"name": "Cross-industry posture", "state": "Generalized", "source": "ONE registry", "actionEnabled": False},
            {"name": "Boundary posture", "state": "Read-only", "source": "UHMI guardrail", "actionEnabled": False},
        ],
        "SYSTEM_HMI": [
            {"name": "System state summary", "state": "Visible", "source": "CODE approved read model", "actionEnabled": False},
            {"name": "Subsystem grouping", "state": "Visible", "source": "UConsole workspace", "actionEnabled": False},
            {"name": "Trend preview", "state": "Visible", "source": "Report projection", "actionEnabled": False},
        ],
        "DEVICE_HMI": [
            {"name": "Device summary card", "state": "Visible", "source": "CODE approved read model", "actionEnabled": False},
            {"name": "Telemetry snapshot", "state": "Visible", "source": "EDGE/LINK via CODE", "actionEnabled": False},
            {"name": "Command surface", "state": "Disabled", "source": "UHMI guardrail", "actionEnabled": False},
        ],
        "ALARM_EVENT_HMI": [
            {"name": "Alarm timeline", "state": "Visible", "source": "Alarm/event projection", "actionEnabled": False},
            {"name": "Event detail", "state": "Visible", "source": "CODE approved read model", "actionEnabled": False},
            {"name": "Acknowledge action", "state": "Disabled", "source": "UHMI guardrail", "actionEnabled": False},
        ],
        "EDGE_LINK_DIAGNOSTICS": [
            {"name": "EDGE status", "state": "Visible", "source": "Diagnostics projection", "actionEnabled": False},
            {"name": "LINK delivery state", "state": "Visible", "source": "Diagnostics projection", "actionEnabled": False},
            {"name": "Connector command", "state": "Disabled", "source": "UHMI guardrail", "actionEnabled": False},
        ],
        "EVIDENCE_REPORTS": [
            {"name": "UCDE evidence reference", "state": "Visible", "source": "UCDE projection", "actionEnabled": False},
            {"name": "Report export readiness", "state": "Visible", "source": "Reports projection", "actionEnabled": False},
            {"name": "Evidence closure", "state": "Disabled", "source": "UHMI guardrail", "actionEnabled": False},
        ],
    }
    purpose_by_key = {
        "HMI_OVERVIEW": "Overview of UHMI read-only operating posture.",
        "SYSTEM_HMI": "System-level HMI context without system control.",
        "DEVICE_HMI": "Device-level HMI context without device control.",
        "ALARM_EVENT_HMI": "Alarm and event HMI context without acknowledgement or mutation.",
        "EDGE_LINK_DIAGNOSTICS": "EDGE and LINK diagnostics without connector commands.",
        "EVIDENCE_REPORTS": "Evidence and report references without evidence closure or export execution.",
    }
    return _section(
        key=item["key"],
        label=item["label"],
        route=item["route"],
        purpose=purpose_by_key[item["key"]],
        rows=rows_by_key[item["key"]],
    )

