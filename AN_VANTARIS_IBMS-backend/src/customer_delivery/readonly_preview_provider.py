"""Customer Delivery / Engineer Installer read-only preview fixtures."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

SCOPE = "CUSTOMER_DELIVERY_GA_R1"
MODE = "read_only"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
APP_NON_DB_TARGET = "192.168.60.21"
DB_ONLY_TARGET = "192.168.60.22"
FUTURE_CONTROL_PATH = "UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device"

SAFETY_FLAGS: Dict[str, Any] = {
    "engineerInstallerConsolePreview": True,
    "customerDeliveryPreview": True,
    "appNonDbTarget": APP_NON_DB_TARGET,
    "dbOnlyTarget": DB_ONLY_TARGET,
    "deploymentExecuted": False,
    "sshExecuted": False,
    "installExecuted": False,
    "uninstallExecuted": False,
    "rollbackExecuted": False,
    "dbMigrationExecuted": False,
    "dbWrite": False,
    "runtimeActivation": False,
    "deviceControl": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "productionActivation": False,
    "runnablePackageGenerated": False,
    "distBuildCommitted": False,
}


def _base_response() -> Dict[str, Any]:
    return {
        "scope": SCOPE,
        "mode": MODE,
        "visualStyle": VISUAL_STYLE,
        **SAFETY_FLAGS,
        "futureControlPath": FUTURE_CONTROL_PATH,
    }


def _readiness(
    package_id: str,
    package_name: str,
    package_role: str,
    target_server: str,
) -> Dict[str, Any]:
    return {
        "packageId": package_id,
        "packageName": package_name,
        "packageRole": package_role,
        "targetServer": target_server,
        "readinessStatus": "READ_ONLY_PREVIEW_READY",
        "customerVisible": True,
        "engineerVisible": True,
        "installActionState": "NOT_EXECUTED",
        "verificationState": "PREVIEW_ONLY",
        "rollbackState": "NOT_EXECUTED",
        "guardrailStatus": "READ_ONLY_NO_INSTALL_NO_DEPLOY_NO_RUNTIME",
        "readOnly": True,
    }


PACKAGE_READINESS: List[Dict[str, Any]] = [
    _readiness("uconsole", "UConsole", "Operations console entry", APP_NON_DB_TARGET),
    _readiness("uhmi", "UHMI", "Unified Human-Machine Interface workspace preview", APP_NON_DB_TARGET),
    _readiness("ucde", "UCDE", "Evidence Center / Audit Evidence Context", APP_NON_DB_TARGET),
    _readiness("customer-delivery", "Customer Delivery", "Customer handoff and installer preview", APP_NON_DB_TARGET),
    _readiness("edge-foundation", "EDGE Foundation", "Shared foundation package readiness reference", APP_NON_DB_TARGET),
    _readiness("vantaris-link", "VANTARIS Link", "Shared LINK foundation package readiness reference", APP_NON_DB_TARGET),
    _readiness("db-foundation", "DB Foundation", "DB-only planning reference", DB_ONLY_TARGET),
    _readiness("contracts", "Contracts", "Shared contract package readiness reference", APP_NON_DB_TARGET),
    _readiness("reports", "Reports", "Read-only report evidence reference", APP_NON_DB_TARGET),
    _readiness("governance-security", "Governance & Security", "Policy and acceptance guardrail reference", APP_NON_DB_TARGET),
]

APP_SERVER_PLAN = {
    "serverIp": APP_NON_DB_TARGET,
    "role": "APP_NON_DB",
    "plannedComponents": [
        "Frontend",
        "Backend",
        "UConsole",
        "UHMI",
        "UCDE",
        "Customer Delivery",
        "Reports",
        "API",
        "EDGE/LINK engineer diagnostics preview",
    ],
    "deploymentExecuted": False,
    "sshExecuted": False,
}

DB_SERVER_PLAN = {
    "serverIp": DB_ONLY_TARGET,
    "role": "DB_ONLY",
    "plannedComponents": ["PostgreSQL", "DB Foundation"],
    "deploymentExecuted": False,
    "sshExecuted": False,
    "migrationExecuted": False,
    "dbWrite": False,
}

CHECKLISTS = {
    "offlinePackage": [
        "Package manifest review",
        "Package count review",
        "Checksum evidence reference",
        "Customer handoff notes review",
    ],
    "precheck": [
        "Server role plan review",
        "Foundation package readiness review",
        "Forbidden artifact review",
        "Acceptance owner review",
    ],
    "installationPlan": [
        "Read-only plan review",
        "No Install",
        "No SSH",
        "No Runtime Activation",
    ],
    "verificationPlan": [
        "Read-only verification plan",
        "No server scan",
        "No external API call",
        "No device connectivity",
    ],
    "rollbackPlan": [
        "Rollback plan preview",
        "No Rollback",
        "No destructive action",
        "Separate approval required",
    ],
    "acceptanceChecklist": [
        "Customer Delivery preview visible",
        "Engineer Installer Console visible",
        "APP server plan visible: 192.168.60.21",
        "DB server plan visible: 192.168.60.22",
        "No Production Activation",
    ],
}


def customer_delivery_preview() -> Dict[str, Any]:
    return {
        **_base_response(),
        "title": "Customer Delivery Preview",
        "readOnlyMode": True,
        "serverPlan": server_plan(),
        "packageReadiness": deepcopy(PACKAGE_READINESS),
        "offlinePackagePreview": CHECKLISTS["offlinePackage"],
        "precheckPreview": CHECKLISTS["precheck"],
        "installationPlanPreview": CHECKLISTS["installationPlan"],
        "verificationPlanPreview": CHECKLISTS["verificationPlan"],
        "rollbackPlanPreview": CHECKLISTS["rollbackPlan"],
        "acceptanceChecklistPreview": CHECKLISTS["acceptanceChecklist"],
    }


def engineer_installer_console() -> Dict[str, Any]:
    return {
        **_base_response(),
        "title": "Engineer Installer Console",
        "readOnlyMode": True,
        "consoleSections": [
            "Offline Package Preview",
            "Precheck Checklist",
            "Installation Plan",
            "Verification Plan",
            "Rollback Plan",
            "Acceptance Checklist",
            "Package Readiness",
            "EDGE / LINK / DB diagnostics preview",
            "Guardrails",
        ],
        "serverPlan": server_plan(),
        "packageReadiness": deepcopy(PACKAGE_READINESS),
        "diagnosticsPreview": diagnostics_preview(),
    }


def server_plan() -> Dict[str, Any]:
    return {
        **_base_response(),
        "appNonDb": deepcopy(APP_SERVER_PLAN),
        "dbOnly": deepcopy(DB_SERVER_PLAN),
    }


def package_readiness() -> Dict[str, Any]:
    return {**_base_response(), "packageReadiness": deepcopy(PACKAGE_READINESS)}


def diagnostics_preview() -> Dict[str, Any]:
    return {
        **_base_response(),
        "diagnosticsPreview": [
            "EDGE / LINK / DB diagnostics preview is read-only.",
            "No real diagnostics executed.",
            "No server scan.",
            "No runtime calls.",
            "No external API calls.",
        ],
    }


def checklist(name: str) -> Dict[str, Any]:
    return {**_base_response(), name: list(CHECKLISTS[name])}


def guardrails() -> Dict[str, Any]:
    return {
        **_base_response(),
        "guardrails": [
            "No SSH",
            "No Install",
            "No uninstall",
            "No Rollback",
            "No DB Migration",
            "No DB Write",
            "No Runtime Activation",
            "No Direct Device Control",
            "No EDGE Command Execution",
            "No LINK Command Execution",
            "No auth / login / JWT / RBAC mutation",
            "No Production Activation",
            "No runnable production package",
            "No dist/build committed",
        ],
    }

