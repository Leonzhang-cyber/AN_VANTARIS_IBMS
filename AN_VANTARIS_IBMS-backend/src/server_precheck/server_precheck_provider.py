"""SERVER-PRECHECK-R1 read-only dual-server audit provider.

This provider returns static planning projections only. It does not perform
SSH, network checks, database connections, deployment, installation, runtime
healthchecks, service setup, EDGE/LINK commands, or device control.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
SCOPE = "SERVER_PRECHECK_R1"
MODULE_ID = "server-precheck"
MODULE_NAME = "Server Precheck"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
PASS_MARKER = "ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS"
APP_SERVER_IP = "192.168.60.21"
DB_SERVER_IP = "192.168.60.22"

READ_ONLY_FLAGS: Dict[str, Any] = {
    "scope": SCOPE,
    "moduleId": MODULE_ID,
    "readOnly": True,
    "sshExecuted": False,
    "deploymentExecuted": False,
    "installExecuted": False,
    "dbConnectionExecuted": False,
    "dbMigrationExecuted": False,
    "dbWriteEnabled": False,
    "healthcheckRuntimeExecuted": False,
    "nginxSetupExecuted": False,
    "pm2SetupExecuted": False,
    "systemdSetupExecuted": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
    "visualStyle": VISUAL_STYLE,
}

SOURCE_REFERENCE_PATHS = [
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1",
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r2",
    "AN_VANTARIS_ONE/registries/foundation-diagnostics-ga-r1",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/security/deployment-profile-security-baseline.v1.md",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/engineering-handoff",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE/config/templates/deployment-profile.vantaris-one.yaml",
    "AN_VANTARIS_ONE/NEXUSAI_GA_R3.md",
    "AN_VANTARIS_ONE/CODE_GA_R1.md",
    "AN_VANTARIS_ONE/ASSET_CONTEXT_GA_R1.md",
]

APP_ROLES = [
    "APP",
    "Web",
    "Backend",
    "Frontend",
    "Console",
    "UHMI",
    "UCDE",
    "UMMS",
    "Reports",
    "Customer Delivery",
    "Foundation Diagnostics",
    "Asset Context",
    "CODE Policy Gate",
    "NexusAI Branch Audit",
]

DB_ROLES = ["PostgreSQL DB only", "backup target planning", "restore target planning"]

GUARDRAILS = [
    "No SSH",
    "No deployment",
    "No install",
    "No DB connection",
    "No DB migration",
    "No DB write",
    "No runtime healthcheck",
    "No Nginx/PM2/systemd setup",
    "No EDGE/LINK command",
    "No device control",
    "No production activation",
]


def common() -> Dict[str, Any]:
    return {
        **READ_ONLY_FLAGS,
        "moduleName": MODULE_NAME,
        "provider": "local-readonly-server-precheck-provider",
        "passMarker": PASS_MARKER,
    }


def source_references() -> Dict[str, Any]:
    limitations: List[str] = []
    statuses: Dict[str, Any] = {}
    refs: List[Dict[str, Any]] = []
    for item in SOURCE_REFERENCE_PATHS:
        path = ROOT / item
        try:
            exists = path.exists()
            content_length = len(path.read_text(encoding="utf-8")) if path.is_file() else 0
            status = "available" if exists else "unavailable"
            if not exists:
                limitations.append(f"Reference source unavailable: {item}")
            statuses[item] = {"integrationStatus": status, "readOnly": True}
            refs.append({"path": item, "exists": exists, "contentLength": content_length, "readOnly": True})
        except Exception as exc:  # pragma: no cover - defensive read-only reference guard
            message = f"Reference source unavailable: {item} ({exc.__class__.__name__})"
            limitations.append(message)
            statuses[item] = {"integrationStatus": "unavailable", "readOnly": True, "reason": message}
            refs.append({"path": item, "exists": False, "contentLength": 0, "readOnly": True})
    return {"sourceReferences": refs, "providerStatuses": statuses, "limitations": limitations}


def server_plan() -> Dict[str, Any]:
    return {
        **common(),
        "appServer": {
            "ip": APP_SERVER_IP,
            "roles": APP_ROLES,
            "prohibitedRoles": [
                "DB primary",
                "DB migration execution in R1",
                "EDGE runtime command",
                "LINK runtime command",
                "Device control",
            ],
            "status": "planning-only",
        },
        "dbServer": {
            "ip": DB_SERVER_IP,
            "roles": DB_ROLES,
            "prohibitedRoles": [
                "Web frontend",
                "Backend app runtime",
                "EDGE/LINK runtime",
                "Device control",
            ],
            "status": "planning-only",
        },
        "networkAssumption": [
            "APP may reach DB only after approved deployment phase",
            "no connection tested in R1",
        ],
    }


def app_server() -> Dict[str, Any]:
    return {
        **common(),
        "ip": APP_SERVER_IP,
        "osRequirement": "Linux server OS/version to be verified during approved access window",
        "cpuRamDiskRecommendation": "4+ CPU cores, 16GB+ RAM, 100GB+ application/log capacity planning",
        "nodePlanningStatus": "planning-only",
        "pythonPlanningStatus": "planning-only",
        "nginxPlanningStatus": "planning-only",
        "pm2PlanningStatus": "planning-only",
        "environmentFileRequirement": ".env secret management to be customer-approved; not modified in R1",
        "portsPlanning": ["80/443 web ingress planning", "backend API port planning", "no port test executed"],
        "sslTlsPlanning": "TLS certificate planning required before production",
        "logDirectoryPlanning": "application, web, audit, and operator logs to be planned",
        "backupArtifactPlanning": "offline package and rollback artifact location planning",
        "status": "planning-only",
    }


def db_server() -> Dict[str, Any]:
    return {
        **common(),
        "ip": DB_SERVER_IP,
        "postgresqlRequirement": "PostgreSQL DB only; version to be verified during approved access window",
        "dbUserRolePlanning": "least-privilege application role planning required",
        "schemaMigrationPlanning": "migration plan required; not executed in R1",
        "backupRestorePlanning": "backup path and restore drill required before GA",
        "networkAccessPlanning": "APP to DB route requires approved firewall and customer IT review",
        "status": "planning-only",
    }


def checklist() -> Dict[str, Any]:
    rows = [
        ("server-os-version", "Server", "server OS/version", "OS release and patch level", "Customer IT"),
        ("disk-space", "Capacity", "disk space", "df report and mount plan", "Engineer"),
        ("cpu-ram", "Capacity", "CPU/RAM", "CPU core and memory inventory", "Engineer"),
        ("network-app-db", "Network", "network route APP->DB", "approved route and firewall record", "Customer IT"),
        ("firewall-ports", "Network", "firewall ports", "ingress/egress matrix", "Security"),
        ("dns-hostname", "Network", "DNS/hostname", "DNS entries and hostnames", "Customer IT"),
        ("tls-cert", "Security", "TLS cert", "certificate chain and expiry evidence", "Security"),
        ("nginx", "Runtime Planning", "Nginx", "Nginx config review package", "Engineer"),
        ("backend-runtime", "Runtime Planning", "backend runtime", "Python/backend runtime plan", "Engineer"),
        ("frontend-static-path", "Runtime Planning", "frontend static path", "static asset path plan", "Engineer"),
        ("pm2-systemd", "Runtime Planning", "PM2/systemd strategy", "service manager decision", "Engineer"),
        ("postgres-version", "DB", "PostgreSQL version", "version evidence", "DB Engineer"),
        ("db-backup-path", "DB", "DB backup path", "backup target evidence", "DB Engineer"),
        ("db-restore-drill", "DB", "DB restore drill", "restore drill record", "DB Engineer"),
        ("env-secret-management", "Security", ".env secret management", "secret handling process", "Security"),
        ("offline-package-integrity", "Delivery", "offline package integrity", "hash and package manifest", "Engineer"),
        ("rollback-plan", "Delivery", "rollback plan", "rollback checklist", "Engineer"),
        ("log-audit-retention", "Operations", "log/audit retention", "retention policy", "Security"),
        ("monitoring", "Operations", "monitoring", "monitoring target plan", "Engineer"),
        ("uat-account-readiness", "UAT", "UAT account readiness", "customer UAT account checklist", "Customer IT"),
    ]
    return {
        **common(),
        "items": [
            {
                "itemId": item_id,
                "category": category,
                "title": title,
                "expectedEvidence": evidence,
                "currentStatus": "not_checked" if category not in {"Delivery"} else "planned",
                "executionStatus": "not_executed",
                "ownerRole": owner,
            }
            for item_id, category, title, evidence, owner in rows
        ],
    }


def blockers() -> Dict[str, Any]:
    rows = [
        ("no-ssh-access", "No SSH/server access performed", "high", "APP/DB", "Read-only local task only", "Schedule approved read-only server access window"),
        ("no-deployment", "No deployment performed", "high", "APP", "Deployment is outside R1", "Approve deployment plan after precheck"),
        ("no-db-connection", "No DB connection tested", "high", "DB", "DB connection is prohibited in R1", "Run approved DB connectivity test later"),
        ("no-db-migration", "No DB migration executed", "high", "DB", "Migration execution is prohibited in R1", "Approve migration plan and rollback"),
        ("no-runtime-healthcheck", "No runtime healthcheck executed", "medium", "APP", "Runtime calls are prohibited in R1", "Run healthchecks after deployment approval"),
        ("no-backup-restore", "No backup/restore drill executed", "medium", "DB", "No DB access in R1", "Perform restore drill before GA"),
        ("no-uat", "No UAT executed", "medium", "APP/DB", "Customer UAT is not part of R1", "Schedule customer UAT"),
        ("no-monitoring", "No production monitoring enabled", "medium", "APP", "No production activation in R1", "Enable monitoring during production readiness phase"),
        ("remote-not-aligned", "Remote branch not aligned with local latest commits", "medium", "Branch", "Local latest preview changes require final review", "Optional push/tag after final review"),
    ]
    return {
        **common(),
        "items": [
            {
                "blockerId": blocker_id,
                "title": title,
                "severity": severity,
                "affectedServer": affected,
                "reason": reason,
                "requiredActionBeforeGA": action,
                "currentStatus": "open",
            }
            for blocker_id, title, severity, affected, reason, action in rows
        ],
    }


def handoff_readiness() -> Dict[str, Any]:
    return {
        **common(),
        "customerHandoffStatus": "READINESS_PREVIEW_ONLY",
        "serverPrecheckStatus": "NOT_EXECUTED",
        "deploymentStatus": "NOT_EXECUTED",
        "dbActivationStatus": "NOT_EXECUTED",
        "productionGaStatus": "NOT_YET",
        "nextRecommendedStep": "approved read-only server access window OR final local push/tag decision",
        "linkedModules": [
            "Customer Delivery",
            "Foundation Diagnostics",
            "Reports",
            "Asset Context",
            "CODE Policy Gate",
            "NexusAI Branch Audit",
        ],
    }


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}


def summary() -> Dict[str, Any]:
    refs = source_references()
    checklist_items = checklist()["items"]
    blocker_items = blockers()["items"]
    return {
        **common(),
        "appServerIp": APP_SERVER_IP,
        "dbServerIp": DB_SERVER_IP,
        "appServerRoleCount": len(APP_ROLES),
        "dbServerRoleCount": len(DB_ROLES),
        "checklistTotal": len(checklist_items),
        "blockersTotal": len(blocker_items),
        "readyForServerAccess": False,
        "readyForDeployment": False,
        "productionGaStatus": "NOT_YET",
        "pushExecuted": False,
        "remoteAligned": False,
        "limitations": refs["limitations"],
        "providerStatuses": refs["providerStatuses"],
        "sourceReferences": refs["sourceReferences"],
    }


def health() -> Dict[str, Any]:
    data = summary()
    return {
        **common(),
        "status": "ok" if not data["limitations"] else "degraded",
        "sourceReferences": data["sourceReferences"],
        "providerStatuses": data["providerStatuses"],
        "serverReachability": "not_checked",
        "runtimeHealthcheck": "not_executed",
        "limitations": data["limitations"],
    }

