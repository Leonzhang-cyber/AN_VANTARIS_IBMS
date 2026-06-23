"""Foundation Diagnostics GA R1 read-only provider."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

SCOPE = "FOUNDATION_DIAGNOSTICS_GA_R1"
MODE = "read_only"
READINESS = "ENGINEER_DIAGNOSTICS_WORKSPACE"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
APP_TARGET = "192.168.60.21"
DB_TARGET = "192.168.60.22"
FUTURE_PATH = "Engineer Workspace -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device"


def common() -> Dict[str, Any]:
    return {
        "scope": SCOPE,
        "mode": MODE,
        "readinessLevel": READINESS,
        "visualStyle": VISUAL_STYLE,
        "engineerDiagnosticsWorkspace": True,
        "appNonDbTarget": APP_TARGET,
        "dbOnlyTarget": DB_TARGET,
        "sshExecuted": False,
        "deploymentExecuted": False,
        "installExecuted": False,
        "uninstallExecuted": False,
        "rollbackExecuted": False,
        "dbConnectionExecuted": False,
        "dbMigrationExecuted": False,
        "dbWrite": False,
        "edgeCommandExecution": False,
        "linkCommandExecution": False,
        "deviceControl": False,
        "runtimeActivation": False,
        "productionActivation": False,
        "futureExecutionPath": FUTURE_PATH,
    }


def _ro(row: Dict[str, Any]) -> Dict[str, Any]:
    value = deepcopy(row)
    value.setdefault("readOnly", True)
    return value


def server_plan() -> Dict[str, Any]:
    return {
        **common(),
        "serverPlan": {
            "appNonDb": {
                "serverIp": APP_TARGET,
                "role": "APP_NON_DB",
                "plannedComponents": [
                    "Frontend",
                    "Backend",
                    "UConsole",
                    "UHMI",
                    "UCDE",
                    "UMMS",
                    "Customer Delivery",
                    "Reports",
                    "API",
                    "EDGE/LINK engineer diagnostics preview",
                ],
                "sshExecuted": False,
                "deploymentExecuted": False,
                "installExecuted": False,
                "runtimeActivation": False,
            },
            "dbOnly": {
                "serverIp": DB_TARGET,
                "role": "DB_ONLY",
                "plannedComponents": ["PostgreSQL", "DB Foundation"],
                "sshExecuted": False,
                "deploymentExecuted": False,
                "dbConnectionExecuted": False,
                "migrationExecuted": False,
                "dbMigrationExecuted": False,
                "dbWrite": False,
            },
        },
    }


PACKAGE_READINESS = [
    _ro({"packageId": "edge-foundation", "packageName": "EDGE Foundation", "category": "Shared Foundation", "sourceType": "foundation_package_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_EDGE_COMMAND"}),
    _ro({"packageId": "vantaris-link", "packageName": "VANTARIS Link", "category": "Shared Foundation", "sourceType": "foundation_package_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_LINK_COMMAND"}),
    _ro({"packageId": "db-foundation", "packageName": "DB Foundation", "category": "Shared Foundation", "sourceType": "db_foundation_reference", "targetServer": DB_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_DB_CONNECTION"}),
    _ro({"packageId": "contracts", "packageName": "Contracts", "category": "Shared Foundation", "sourceType": "contract_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_RUNTIME_EXECUTION"}),
    _ro({"packageId": "uconsole", "packageName": "UConsole", "category": "Application", "sourceType": "consumer_workspace", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_DEPLOYMENT"}),
    _ro({"packageId": "uhmi", "packageName": "UHMI", "category": "Application", "sourceType": "read_only_linkage", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_DEVICE_CONTROL"}),
    _ro({"packageId": "ucde", "packageName": "UCDE", "category": "Application", "sourceType": "audit_evidence_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_EVIDENCE_WRITE"}),
    _ro({"packageId": "umms", "packageName": "UMMS", "category": "Application", "sourceType": "maintenance_workspace_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_WORK_ORDER_WRITE"}),
    _ro({"packageId": "customer-delivery", "packageName": "Customer Delivery", "category": "Application", "sourceType": "handoff_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_INSTALL"}),
    _ro({"packageId": "reports", "packageName": "Reports", "category": "Application", "sourceType": "report_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_REPORT_RUNTIME_GENERATION"}),
    _ro({"packageId": "governance-security", "packageName": "Governance & Security", "category": "Policy", "sourceType": "guardrail_reference", "targetServer": APP_TARGET, "readinessStatus": "READ_ONLY_READY", "customerVisible": True, "engineerVisible": True, "installActionState": "NOT_EXECUTED", "diagnosticState": "PREVIEW_ONLY", "rollbackState": "NOT_EXECUTED", "guardrailStatus": "NO_AUTH_RBAC_MUTATION"}),
]


def package_readiness() -> Dict[str, Any]:
    return {**common(), "packageReadiness": deepcopy(PACKAGE_READINESS)}


def edge_readiness() -> Dict[str, Any]:
    return {**common(), "edgeReadiness": {"packageAvailable": True, "connectorMatrixReferenced": True, "offlineInstallReferenced": True, "hardwareKeyGuardReferenced": True, "localBufferReferenced": True, "diagnosticsPreviewOnly": True, "commandExecution": False, "deviceConnection": False}}


def link_readiness() -> Dict[str, Any]:
    return {**common(), "linkReadiness": {"packageAvailable": True, "ingressReferenced": True, "queueReferenced": True, "retryDlqReferenced": True, "ackReferenced": True, "diagnosticsPreviewOnly": True, "commandExecution": False}}


def db_readiness() -> Dict[str, Any]:
    return {**common(), "dbReadiness": {"packageAvailable": True, "postgresTarget": DB_TARGET, "migrationPlanReferenced": True, "backupRestoreReferenced": True, "connectionExecuted": False, "migrationExecuted": False, "dbWrite": False}}


def contracts_readiness() -> Dict[str, Any]:
    return {**common(), "contractsReadiness": {"packageAvailable": True, "apiContractsReferenced": True, "errorResponseReferenced": True, "securityBoundaryReferenced": True, "compatibilityMappingReferenced": True, "runtimeExecution": False}}


def healthcheck_preview() -> Dict[str, Any]:
    rows = [
        ("HC-APP-001", "APP role plan review", "UConsole", APP_TARGET, "Plan visible"),
        ("HC-EDGE-001", "EDGE readiness reference", "EDGE Foundation", APP_TARGET, "Reference present"),
        ("HC-LINK-001", "LINK readiness reference", "VANTARIS Link", APP_TARGET, "Reference present"),
        ("HC-DB-001", "DB target planning review", "DB Foundation", DB_TARGET, "Plan visible"),
        ("HC-CON-001", "Contract compatibility review", "Contracts", APP_TARGET, "Reference present"),
    ]
    return {**common(), "healthcheckPreview": [_ro({"checkId": a, "checkName": b, "packageName": c, "targetServer": d, "expectedResult": e, "executionState": "NOT_EXECUTED", "previewStatus": "PREVIEW_READY"}) for a, b, c, d, e in rows]}


def package_integrity() -> Dict[str, Any]:
    return {**common(), "packageIntegrityPreview": [_ro({"packageName": item["packageName"], "targetServer": item["targetServer"], "manifestReferenced": True, "checksumPreview": "REFERENCE_ONLY", "integrityState": "PREVIEW_ONLY"}) for item in PACKAGE_READINESS]}


def rollback_readiness() -> Dict[str, Any]:
    return {**common(), "rollbackReadiness": [_ro({"rollbackItem": f"{item['packageName']} rollback plan", "packageName": item["packageName"], "targetServer": item["targetServer"], "rollbackPlanReferenced": True, "rollbackExecuted": False}) for item in PACKAGE_READINESS[:6]]}


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": ["No SSH", "No Deployment", "No Install", "No Uninstall", "No Rollback", "No DB Connection", "No DB Migration", "No DB Write", "No EDGE Command Execution", "No LINK Command Execution", "No Device Control", "No Runtime Activation", "No Production Activation"]}


def offline_checklist() -> Dict[str, Any]:
    return {**common(), "offlineChecklist": ["Package manifest preview", "Server plan preview", "Foundation readiness preview", "Healthcheck Preview", "Package Integrity Preview", "Rollback Readiness", "No-execution guardrails"]}


def workspace() -> Dict[str, Any]:
    data = {
        **common(),
        "title": "Foundation Diagnostics Workspace",
        "overviewCards": [
            {"label": "APP Server Plan", "value": APP_TARGET, "status": "Preview"},
            {"label": "DB Server Plan", "value": DB_TARGET, "status": "Preview"},
            {"label": "EDGE Readiness", "value": "Ready", "status": "Reference"},
            {"label": "LINK Readiness", "value": "Ready", "status": "Reference"},
            {"label": "DB Foundation Readiness", "value": "Ready", "status": "Reference"},
            {"label": "Contracts Readiness", "value": "Ready", "status": "Reference"},
            {"label": "Offline Package Readiness", "value": "Ready", "status": "Preview"},
            {"label": "Rollback Readiness", "value": "Ready", "status": "Preview"},
        ],
        **server_plan(),
        **package_readiness(),
        **edge_readiness(),
        **link_readiness(),
        **db_readiness(),
        **contracts_readiness(),
        **offline_checklist(),
        **healthcheck_preview(),
        **package_integrity(),
        **rollback_readiness(),
        **guardrails(),
    }
    return data


def section(name: str) -> Dict[str, Any]:
    sections = {
        "workspace": workspace,
        "overview": workspace,
        "server-plan": server_plan,
        "package-readiness": package_readiness,
        "edge-readiness": edge_readiness,
        "link-readiness": link_readiness,
        "db-readiness": db_readiness,
        "contracts-readiness": contracts_readiness,
        "offline-checklist": offline_checklist,
        "healthcheck-preview": healthcheck_preview,
        "package-integrity": package_integrity,
        "rollback-readiness": rollback_readiness,
        "guardrails": guardrails,
    }
    return sections.get(name, workspace)()
