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

R2B_SCOPE = "UHMI_GA_R2B"
R2B_MODE = "read_only"
R2B_VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
FUTURE_CONTROL_PATH = "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device"
R2B_PANELS = [
    "Overview",
    "System Panels",
    "Device Panels",
    "Mimic Panels",
    "Status View",
    "Event Context",
    "Evidence Context",
    "Guardrails",
    "Future Control Path",
]

SYSTEM_CONTEXTS: list[dict[str, Any]] = [
    {
        "systemId": "sys-building",
        "systemName": "Building Systems",
        "category": "building_operations",
        "healthStatus": "healthy",
        "visibleDevices": 42,
        "activeEvents": 3,
        "panelCount": 6,
        "evidenceCount": 14,
        "readOnly": True,
    },
    {
        "systemId": "sys-facility",
        "systemName": "Facility Systems",
        "category": "facility_operations",
        "healthStatus": "attention",
        "visibleDevices": 31,
        "activeEvents": 5,
        "panelCount": 5,
        "evidenceCount": 9,
        "readOnly": True,
    },
    {
        "systemId": "sys-security",
        "systemName": "Security Systems",
        "category": "security_operations",
        "healthStatus": "healthy",
        "visibleDevices": 28,
        "activeEvents": 2,
        "panelCount": 4,
        "evidenceCount": 18,
        "readOnly": True,
    },
    {
        "systemId": "sys-energy",
        "systemName": "Energy Systems",
        "category": "energy_operations",
        "healthStatus": "healthy",
        "visibleDevices": 24,
        "activeEvents": 4,
        "panelCount": 5,
        "evidenceCount": 11,
        "readOnly": True,
    },
    {
        "systemId": "sys-data-center",
        "systemName": "Data Center Systems",
        "category": "critical_environment",
        "healthStatus": "monitoring",
        "visibleDevices": 36,
        "activeEvents": 6,
        "panelCount": 7,
        "evidenceCount": 21,
        "readOnly": True,
    },
    {
        "systemId": "sys-utility",
        "systemName": "Utility Systems",
        "category": "utility_operations",
        "healthStatus": "healthy",
        "visibleDevices": 19,
        "activeEvents": 1,
        "panelCount": 3,
        "evidenceCount": 8,
        "readOnly": True,
    },
]

DEVICE_CONTEXTS: list[dict[str, Any]] = [
    {
        "deviceId": "dev-air-handler-01",
        "deviceName": "Air Handler 01",
        "systemName": "Building Systems",
        "location": "Level 12 Plant Room",
        "status": "online",
        "lastSeen": "2026-06-23T00:15:00Z",
        "eventCount": 1,
        "panelAvailable": True,
        "controlState": "disabled/read-only",
    },
    {
        "deviceId": "dev-chiller-02",
        "deviceName": "Chiller 02",
        "systemName": "Facility Systems",
        "location": "Central Utility Plant",
        "status": "attention",
        "lastSeen": "2026-06-23T00:14:00Z",
        "eventCount": 3,
        "panelAvailable": True,
        "controlState": "disabled/read-only",
    },
    {
        "deviceId": "dev-access-panel-04",
        "deviceName": "Access Panel 04",
        "systemName": "Security Systems",
        "location": "East Lobby",
        "status": "online",
        "lastSeen": "2026-06-23T00:13:00Z",
        "eventCount": 0,
        "panelAvailable": True,
        "controlState": "disabled/read-only",
    },
    {
        "deviceId": "dev-meter-main-01",
        "deviceName": "Main Energy Meter",
        "systemName": "Energy Systems",
        "location": "Main Switch Room",
        "status": "online",
        "lastSeen": "2026-06-23T00:12:00Z",
        "eventCount": 2,
        "panelAvailable": True,
        "controlState": "disabled/read-only",
    },
    {
        "deviceId": "dev-crac-03",
        "deviceName": "CRAC Unit 03",
        "systemName": "Data Center Systems",
        "location": "Data Hall B",
        "status": "monitoring",
        "lastSeen": "2026-06-23T00:11:00Z",
        "eventCount": 4,
        "panelAvailable": True,
        "controlState": "disabled/read-only",
    },
]

MIMIC_PANELS: list[dict[str, Any]] = [
    {
        "panelId": "mimic-building-summary",
        "panelName": "Building Summary",
        "systemName": "Building Systems",
        "previewType": "status_grid",
        "status": "available",
        "readOnly": True,
        "controlsDisabled": True,
    },
    {
        "panelId": "mimic-facility-loop",
        "panelName": "Facility Loop",
        "systemName": "Facility Systems",
        "previewType": "process_overview",
        "status": "available",
        "readOnly": True,
        "controlsDisabled": True,
    },
    {
        "panelId": "mimic-energy-flow",
        "panelName": "Energy Flow",
        "systemName": "Energy Systems",
        "previewType": "flow_preview",
        "status": "available",
        "readOnly": True,
        "controlsDisabled": True,
    },
    {
        "panelId": "mimic-data-center-health",
        "panelName": "Data Center Health",
        "systemName": "Data Center Systems",
        "previewType": "thermal_status",
        "status": "available",
        "readOnly": True,
        "controlsDisabled": True,
    },
]

EVENT_CONTEXTS: list[dict[str, Any]] = [
    {
        "eventId": "evt-uhmi-001",
        "severity": "medium",
        "title": "Chiller efficiency drift",
        "sourceSystem": "Facility Systems",
        "linkedDevice": "Chiller 02",
        "timestamp": "2026-06-23T00:10:00Z",
        "status": "observed",
        "evidenceLinked": True,
    },
    {
        "eventId": "evt-uhmi-002",
        "severity": "low",
        "title": "Energy meter threshold notice",
        "sourceSystem": "Energy Systems",
        "linkedDevice": "Main Energy Meter",
        "timestamp": "2026-06-23T00:08:00Z",
        "status": "triage_ready",
        "evidenceLinked": True,
    },
    {
        "eventId": "evt-uhmi-003",
        "severity": "high",
        "title": "Data hall thermal watch",
        "sourceSystem": "Data Center Systems",
        "linkedDevice": "CRAC Unit 03",
        "timestamp": "2026-06-23T00:06:00Z",
        "status": "monitoring",
        "evidenceLinked": True,
    },
]

EVIDENCE_CONTEXTS: list[dict[str, Any]] = [
    {
        "evidenceId": "evd-uhmi-001",
        "type": "event_snapshot",
        "linkedObject": "evt-uhmi-001",
        "source": "UCDE projection",
        "timestamp": "2026-06-23T00:10:30Z",
        "integrityStatus": "linked",
        "viewOnly": True,
    },
    {
        "evidenceId": "evd-uhmi-002",
        "type": "device_status",
        "linkedObject": "dev-meter-main-01",
        "source": "CODE projection",
        "timestamp": "2026-06-23T00:08:30Z",
        "integrityStatus": "linked",
        "viewOnly": True,
    },
    {
        "evidenceId": "evd-uhmi-003",
        "type": "panel_capture",
        "linkedObject": "mimic-data-center-health",
        "source": "Reports projection",
        "timestamp": "2026-06-23T00:06:30Z",
        "integrityStatus": "linked",
        "viewOnly": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _guardrails() -> dict[str, Any]:
    return {
        "scope": R2B_SCOPE,
        "mode": R2B_MODE,
        "visualStyle": R2B_VISUAL_STYLE,
        "controlEnabled": False,
        "readOnly": True,
        "runtimeActivation": False,
        "deviceWrite": False,
        "dbWrite": False,
        "edgeCommandExecution": False,
        "linkCommandExecution": False,
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
        "futureControlPath": FUTURE_CONTROL_PATH,
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
        "futureControlledActionPath": FUTURE_CONTROL_PATH,
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


def _summary_metrics() -> list[dict[str, Any]]:
    return [
        {"label": "Systems Monitored", "value": len(SYSTEM_CONTEXTS), "tone": "teal"},
        {"label": "Devices Visible", "value": sum(item["visibleDevices"] for item in SYSTEM_CONTEXTS), "tone": "mint"},
        {"label": "Active Events", "value": sum(item["activeEvents"] for item in SYSTEM_CONTEXTS), "tone": "amber"},
        {"label": "Panels Available", "value": len(R2B_PANELS), "tone": "blue"},
        {"label": "Evidence Records", "value": sum(item["evidenceCount"] for item in SYSTEM_CONTEXTS), "tone": "violet"},
        {"label": "Guardrails Active", "value": 8, "tone": "green"},
    ]


def get_workspace() -> dict[str, Any]:
    data: dict[str, Any] = {
        "workspaceName": "UHMI Workspace",
        "baseline": "UHMI-GA-R2A",
        "panels": R2B_PANELS,
        "summaryCards": _summary_metrics(),
        "systemContexts": SYSTEM_CONTEXTS,
        "deviceContexts": DEVICE_CONTEXTS,
        "mimicPanels": MIMIC_PANELS,
        "eventContexts": EVENT_CONTEXTS,
        "evidenceContexts": EVIDENCE_CONTEXTS,
        "guardrails": get_guardrails()["guardrails"],
    }
    data.update(_guardrails())
    return data


def get_status() -> dict[str, Any]:
    data: dict[str, Any] = {
        "workspaceStatus": "frozen_local_skeleton",
        "systemsMonitored": len(SYSTEM_CONTEXTS),
        "devicesVisible": sum(item["visibleDevices"] for item in SYSTEM_CONTEXTS),
        "activeEvents": sum(item["activeEvents"] for item in SYSTEM_CONTEXTS),
        "panelsAvailable": len(R2B_PANELS),
        "evidenceRecords": sum(item["evidenceCount"] for item in SYSTEM_CONTEXTS),
        "guardrailsActive": 8,
    }
    data.update(_guardrails())
    return data


def get_panels() -> dict[str, Any]:
    data: dict[str, Any] = {
        "panels": [{"panelName": name, "readOnly": True, "controlsDisabled": True} for name in R2B_PANELS],
        "mimicPanels": MIMIC_PANELS,
    }
    data.update(_guardrails())
    return data


def get_systems() -> dict[str, Any]:
    data: dict[str, Any] = {"systemContexts": SYSTEM_CONTEXTS}
    data.update(_guardrails())
    return data


def get_devices() -> dict[str, Any]:
    data: dict[str, Any] = {"deviceContexts": DEVICE_CONTEXTS}
    data.update(_guardrails())
    return data


def get_events() -> dict[str, Any]:
    data: dict[str, Any] = {"eventContexts": EVENT_CONTEXTS}
    data.update(_guardrails())
    return data


def get_evidence() -> dict[str, Any]:
    data: dict[str, Any] = {"evidenceContexts": EVIDENCE_CONTEXTS}
    data.update(_guardrails())
    return data


def get_guardrails() -> dict[str, Any]:
    data: dict[str, Any] = {
        "guardrails": [
            {"label": "Read-only Mode", "active": True},
            {"label": "No Direct Device Control", "active": True},
            {"label": "No Runtime Activation", "active": True},
            {"label": "No DB Write", "active": True},
            {"label": "No EDGE Command Execution", "active": True},
            {"label": "No LINK Command Execution", "active": True},
            {"label": "No NEXUS AI Execution", "active": True},
            {"label": "Future Control Path Requires Policy Approval", "active": True},
        ],
        "futureControlPath": FUTURE_CONTROL_PATH,
        "futureControlStatus": "Future-only / Requires Policy Approval",
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
