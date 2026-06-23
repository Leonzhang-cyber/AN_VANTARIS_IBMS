"""SERVER-PRECHECK-R2 read-only access window plan provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
SCOPE = "SERVER_PRECHECK_R2"
MODULE_ID = "server-access-window-plan"
MODULE_NAME = "Server Access Window Plan"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
PASS_MARKER = "ONE_SERVER_PRECHECK_R2_READONLY_ACCESS_WINDOW_PLAN_PASS"
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
    "AN_VANTARIS_ONE/SERVER_PRECHECK_R1.md",
    "AN_VANTARIS_ONE/registries/server-precheck-r1",
    "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md",
    "AN_VANTARIS_ONE/registries/local-release-index-r1",
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1",
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r2",
    "AN_VANTARIS_ONE/registries/foundation-diagnostics-ga-r1",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/security/deployment-profile-security-baseline.v1.md",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/engineering-handoff",
    "deployment/prod-ga/customer-delivery/checklists",
    "deployment/prod-ga/customer-delivery/scripts",
]

GUARDRAILS = [
    "No SSH in R2",
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
        "provider": "local-readonly-server-access-window-plan-provider",
        "planningMode": "planning-only",
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
        except Exception as exc:  # pragma: no cover
            message = f"Reference source unavailable: {item} ({exc.__class__.__name__})"
            limitations.append(message)
            statuses[item] = {"integrationStatus": "unavailable", "readOnly": True, "reason": message}
            refs.append({"path": item, "exists": False, "contentLength": 0, "readOnly": True})
    return {"sourceReferences": refs, "providerStatuses": statuses, "limitations": limitations}


def access_window() -> Dict[str, Any]:
    return {
        **common(),
        "proposedWindowStatus": "NOT_SCHEDULED",
        "requiredApprovers": [
            "Customer IT owner",
            "Security owner",
            "Application engineer",
            "DB engineer",
            "Delivery manager",
        ],
        "accessMode": [
            "read-only terminal access only after explicit approval",
            "no sudo unless separately approved",
            "no write command",
            "no package install",
            "no service restart",
        ],
        "sessionEvidence": [
            "terminal transcript",
            "command output capture",
            "timestamped checklist",
            "screenshots optional",
            "UCDE evidence record planned, not written",
        ],
        "r2Status": {"planningOnly": True, "sshExecutable": False, "deploymentExecutable": False},
    }


def approval_boundary() -> Dict[str, Any]:
    rows = [
        ("customer-app-access", "Customer IT owner", f"Customer permission to access {APP_SERVER_IP}", "access window"),
        ("customer-db-access", "Customer IT owner", f"Customer permission to access {DB_SERVER_IP}", "access window"),
        ("ssh-account", "Security owner", "SSH account confirmation", "credential handoff"),
        ("readonly-command-list", "Application engineer", "Read-only command list approval", "R3 execution candidate"),
        ("no-db-mutation", "DB engineer", "No DB mutation approval boundary", "DB server observation"),
        ("evidence-capture", "Delivery manager", "Evidence capture approval", "session record"),
        ("stop-conditions", "Security owner", "Stop condition acknowledgement", "session start"),
    ]
    return {
        **common(),
        "items": [
            {
                "approvalId": approval_id,
                "approverRole": role,
                "approvalPurpose": purpose,
                "requiredBefore": required_before,
                "status": "pending",
                "notes": "Required before any actual read-only server access.",
            }
            for approval_id, role, purpose, required_before in rows
        ],
    }


def allowed_readonly_commands() -> Dict[str, Any]:
    """Return allowed read-only commands as plan text only."""
    app_identity = ["hostname", "date", "whoami", "uname -a"]
    app_resources = ["df -h", "free -h", "uptime", "ip addr show", "ss -tulpen"]
    app_versions = ["nginx -v", "node -v", "npm -v", "python3 --version", "pm2 list", "systemctl status nginx", "systemctl status vantaris-app"]
    db_identity = ["hostname", "date", "whoami", "uname -a"]
    db_resources = ["df -h", "free -h", "uptime", "ip addr show", "ss -tulpen"]
    db_versions = ["psql --version", "systemctl status postgresql", "pg_isready"]
    return {
        **common(),
        "catalogName": "allowed read-only commands",
        "items": [
            {
                "commandGroup": "identity",
                "commandPurpose": "Confirm server identity and session account.",
                "appServerAllowedCommands": app_identity,
                "dbServerAllowedCommands": db_identity,
                "outputEvidence": "server identity output",
                "forbiddenVariants": ["sudo hostnamectl set-hostname", "user modification", "file write"],
                "executionStatus": "planned read-only commands, not executed in R2",
            },
            {
                "commandGroup": "resources",
                "commandPurpose": "Observe OS resource and listener posture.",
                "appServerAllowedCommands": app_resources,
                "dbServerAllowedCommands": db_resources,
                "outputEvidence": "OS/resource and port/listener output",
                "forbiddenVariants": ["network mutation", "firewall mutation", "runtime call"],
                "executionStatus": "planned read-only commands, not executed in R2",
            },
            {
                "commandGroup": "versions",
                "commandPurpose": "Observe installed package and service status without restart.",
                "appServerAllowedCommands": app_versions,
                "dbServerAllowedCommands": db_versions,
                "outputEvidence": "package version and service status output",
                "forbiddenVariants": ["systemctl restart", "pm2 restart", "nginx -s reload", "package install"],
                "executionStatus": "planned read-only commands, not executed in R2",
            },
        ],
    }


def evidence_capture() -> Dict[str, Any]:
    return {
        **common(),
        "evidencePlanStatus": "PLANNED_NOT_CAPTURED",
        "evidenceItems": [
            "access approval record",
            "command transcript",
            "server identity output",
            "OS/resource output",
            "port/listener output",
            "package version output",
            "DB readiness output",
            "blocker log",
            "R3 readiness decision",
        ],
        "ucdeEvidenceWrite": False,
        "reportsExport": False,
    }


def stop_conditions() -> Dict[str, Any]:
    rows = [
        ("unexpected-server", "Login lands on unexpected server", "hostname or banner mismatch", "Stop session and notify Customer IT", "high"),
        ("unexpected-sudo", "Account has unexpected sudo/root", "sudo/root detected beyond approval", "Stop and request security review", "high"),
        ("customer-stop", "Customer says stop", "verbal or written stop request", "Stop immediately", "high"),
        ("production-risk", "Output shows production workload risk", "active workload risk appears", "Stop and document blocker", "high"),
        ("db-mutation-required", "DB mutation would be required", "write or migration needed", "Do not proceed in R2/R3", "high"),
        ("service-restart-required", "Service restart would be required", "restart needed for information", "Stop and escalate", "high"),
        ("secrets-exposed", "Credentials/secrets exposure detected", "secret material appears", "Stop capture and follow security process", "high"),
        ("unapproved-command", "Any command not on approved list is needed", "new command required", "Pause for approval", "medium"),
        ("network-instability", "Network instability", "session unstable or incomplete", "Stop and reschedule", "medium"),
        ("security-withdraws", "Security owner withdraws approval", "approval withdrawn", "Stop immediately", "high"),
    ]
    return {
        **common(),
        "items": [
            {"conditionId": cid, "title": title, "trigger": trigger, "requiredAction": action, "severity": severity}
            for cid, title, trigger, action, severity in rows
        ],
    }


def r3_readiness() -> Dict[str, Any]:
    return {
        **common(),
        "r3Candidate": "SERVER-PRECHECK-R3 Actual Approved Read-only Server Observation",
        "readyForR3": False,
        "prerequisites": [
            "written approval",
            "access window scheduled",
            "accounts verified",
            "command list approved",
            "evidence folder prepared",
            "stop conditions accepted",
        ],
        "blockers": [
            "No access window scheduled",
            "No approval captured",
            "No credentials validated",
            "No evidence capture target confirmed",
        ],
    }


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}


def summary() -> Dict[str, Any]:
    refs = source_references()
    return {
        **common(),
        "appServerIp": APP_SERVER_IP,
        "dbServerIp": DB_SERVER_IP,
        "accessWindowStatus": "PLANNING_ONLY",
        "approvalsRequired": len(approval_boundary()["items"]),
        "allowedCommandCount": sum(
            len(item["appServerAllowedCommands"]) + len(item["dbServerAllowedCommands"])
            for item in allowed_readonly_commands()["items"]
        ),
        "forbiddenActionCount": len(GUARDRAILS),
        "evidenceCaptureItems": len(evidence_capture()["evidenceItems"]),
        "stopConditionCount": len(stop_conditions()["items"]),
        "readyForR3": False,
        "readyForSSH": False,
        "readyForDeployment": False,
        "productionGaStatus": "NOT_YET",
        "limitations": refs["limitations"],
        "sourceReferences": refs["sourceReferences"],
        "providerStatuses": refs["providerStatuses"],
    }


def health() -> Dict[str, Any]:
    data = summary()
    return {
        **common(),
        "status": "ok" if not data["limitations"] else "degraded",
        "sourceReferences": data["sourceReferences"],
        "providerStatuses": data["providerStatuses"],
        "accessWindowStatus": "PLANNING_ONLY",
        "serverReachability": "not_checked",
        "runtimeHealthcheck": "not_executed",
        "limitations": data["limitations"],
    }
