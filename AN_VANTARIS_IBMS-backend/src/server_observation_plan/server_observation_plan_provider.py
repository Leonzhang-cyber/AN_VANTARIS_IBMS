"""SERVER-PRECHECK-R3 actual approved read-only server observation plan provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
SCOPE = "SERVER_PRECHECK_R3"
MODULE_ID = "server-observation-plan"
MODULE_NAME = "Server Observation Plan"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
PASS_MARKER = "ONE_SERVER_PRECHECK_R3_ACTUAL_READONLY_OBSERVATION_PLAN_PASS"
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
    "actualObservationExecuted": False,
    "visualStyle": VISUAL_STYLE,
}

SOURCE_REFERENCE_PATHS = [
    "AN_VANTARIS_ONE/SERVER_PRECHECK_R1.md",
    "AN_VANTARIS_ONE/SERVER_PRECHECK_R2.md",
    "AN_VANTARIS_ONE/registries/server-precheck-r1",
    "AN_VANTARIS_ONE/registries/server-precheck-r2",
    "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md",
    "AN_VANTARIS_ONE/registries/local-release-index-r1",
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r1",
    "AN_VANTARIS_ONE/registries/customer-delivery-ga-r2",
    "AN_VANTARIS_ONE/registries/foundation-diagnostics-ga-r1",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/security/deployment-profile-security-baseline.v1.md",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/engineering-handoff",
    "deployment/prod-ga/customer-delivery/checklists",
]

GUARDRAILS = [
    "No SSH executed in R3 planning",
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
    "Actual server observation requires explicit separate approval",
]


def common() -> Dict[str, Any]:
    return {
        **READ_ONLY_FLAGS,
        "moduleName": MODULE_NAME,
        "provider": "local-readonly-server-observation-plan-provider",
        "planName": "actual approved read-only server observation plan",
        "planningMode": "planned-only",
        "executionStatus": "not executed in R3",
        "approvalStatus": "separate approval required",
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


def execution_sequence() -> Dict[str, Any]:
    rows = [
        ("r3-step-01", "Confirm written approval and access window.", "APP/DB", "approval record"),
        ("r3-step-02", "Start transcript capture.", "APP/DB", "transcript file header"),
        ("r3-step-03", "Observe APP server identity and resources.", APP_SERVER_IP, "APP identity and resource output"),
        ("r3-step-04", "Observe APP server network/listeners/package versions.", APP_SERVER_IP, "APP listener and version output"),
        ("r3-step-05", "Observe APP server service status without restart.", APP_SERVER_IP, "APP service status output"),
        ("r3-step-06", "Observe DB server identity and resources.", DB_SERVER_IP, "DB identity and resource output"),
        ("r3-step-07", "Observe DB server PostgreSQL package/status only.", DB_SERVER_IP, "DB PostgreSQL package/status output"),
        ("r3-step-08", "Capture blocker notes.", "APP/DB", "blocker list"),
        ("r3-step-09", "Stop if any stop condition is triggered.", "APP/DB", "stop condition log"),
        ("r3-step-10", "Close evidence package.", "APP/DB", "final R3 observation decision"),
    ]
    return {
        **common(),
        "section": "execution sequence",
        "items": [
            {
                "stepId": step_id,
                "title": title,
                "targetServer": target,
                "plannedOnly": True,
                "executedInR3": False,
                "allowedOnlyAfterApproval": True,
                "evidenceOutput": evidence,
            }
            for step_id, title, target, evidence in rows
        ],
    }


def _planned_command(command_id: str, command: str, purpose: str, forbidden_variants: List[str], db_mutation: bool = False) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "commandId": command_id,
        "command": command,
        "purpose": purpose,
        "plannedOnly": True,
        "executedInR3": False,
        "readOnly": True,
        "forbiddenVariants": forbidden_variants,
    }
    if db_mutation is not None:
        item["dbMutation"] = db_mutation
    return item


def app_server_observation() -> Dict[str, Any]:
    forbidden = ["service lifecycle change", "package install", "configuration edit", "file write", "runtime trigger"]
    commands = [
        ("app-identity-hostname", "hostname", "Confirm APP server host identity."),
        ("app-identity-date", "date", "Capture timestamp context."),
        ("app-identity-user", "whoami", "Confirm session account."),
        ("app-os", "uname -a", "Observe operating system release."),
        ("app-disk", "df -h", "Observe disk capacity."),
        ("app-memory", "free -h", "Observe memory capacity."),
        ("app-uptime", "uptime", "Observe uptime."),
        ("app-network", "ip addr show", "Observe interface assignment."),
        ("app-listeners", "ss -tulpen", "Observe listening ports."),
        ("app-nginx-version", "nginx -v", "Observe Nginx version."),
        ("app-node-version", "node -v", "Observe Node.js version."),
        ("app-npm-version", "npm -v", "Observe npm version."),
        ("app-python-version", "python3 --version", "Observe Python version."),
        ("app-pm2-list", "pm2 list", "Observe PM2 process list."),
        ("app-nginx-status", "systemctl status nginx --no-pager", "Observe Nginx status without restart."),
        ("app-vantaris-status", "systemctl status vantaris-app --no-pager", "Observe VANTARIS app service status without restart."),
    ]
    return {
        **common(),
        "section": "app server observation",
        "target": {"ip": APP_SERVER_IP, "role": "APP / Web / Backend / Frontend / Console"},
        "plannedCommands": [
            _planned_command(command_id, command, purpose, forbidden, False)
            for command_id, command, purpose in commands
        ],
    }


def db_server_observation() -> Dict[str, Any]:
    forbidden = ["interactive DB mutation", "schema change", "table change", "data write", "destructive SQL"]
    commands = [
        ("db-identity-hostname", "hostname", "Confirm DB server host identity."),
        ("db-identity-date", "date", "Capture timestamp context."),
        ("db-identity-user", "whoami", "Confirm session account."),
        ("db-os", "uname -a", "Observe operating system release."),
        ("db-disk", "df -h", "Observe disk capacity."),
        ("db-memory", "free -h", "Observe memory capacity."),
        ("db-uptime", "uptime", "Observe uptime."),
        ("db-network", "ip addr show", "Observe interface assignment."),
        ("db-listeners", "ss -tulpen", "Observe listening ports."),
        ("db-psql-version", "psql --version", "Observe PostgreSQL client package version only."),
        ("db-postgresql-status", "systemctl status postgresql --no-pager", "Observe PostgreSQL service status without restart."),
        ("db-pg-ready", "pg_isready", "Observe readiness command plan without opening DB session."),
    ]
    return {
        **common(),
        "section": "db server observation",
        "target": {"ip": DB_SERVER_IP, "role": "DB only"},
        "plannedCommands": [
            _planned_command(command_id, command, purpose, forbidden, False)
            for command_id, command, purpose in commands
        ],
    }


def evidence_package() -> Dict[str, Any]:
    return {
        **common(),
        "section": "evidence package",
        "evidencePackageStatus": "PLANNED_NOT_CAPTURED",
        "items": [
            "approval record",
            "transcript file",
            "APP server identity output",
            "APP server resource output",
            "APP server listener output",
            "APP package/runtime version output",
            "DB server identity output",
            "DB server PostgreSQL package/status output",
            "blocker list",
            "stop condition log",
            "final R3 observation decision",
        ],
        "ucdeEvidenceWrite": False,
        "reportsExport": False,
        "evidenceStorage": "planned local folder, not created in R3",
    }


def stop_conditions() -> Dict[str, Any]:
    rows = [
        ("unexpected-server-identity", "high", "unexpected server identity", "production access may be misdirected"),
        ("unexpected-root-sudo", "high", "unexpected root/sudo requirement", "privilege boundary risk"),
        ("unapproved-command-needed", "high", "command not on approved list is needed", "approval boundary incomplete"),
        ("secret-exposure", "high", "secret/credential exposure detected", "sensitive material risk"),
        ("customer-security-stop", "high", "customer/security owner says stop", "approval withdrawn"),
        ("production-workload-risk", "high", "production workload risk observed", "production workload risk"),
        ("service-restart-needed", "high", "service restart needed", "runtime change would be required"),
        ("db-mutation-needed", "high", "DB mutation needed", "database write risk"),
        ("network-instability", "medium", "network instability", "evidence reliability risk"),
        ("unclear-server-role", "medium", "unclear server role", "target classification uncertainty"),
        ("evidence-capture-blocked", "medium", "evidence capture cannot continue", "evidence package incomplete"),
    ]
    return {
        **common(),
        "section": "stop conditions",
        "items": [
            {
                "conditionId": condition_id,
                "severity": severity,
                "trigger": trigger,
                "requiredAction": "stop observation and escalate",
                "productionImpact": impact,
            }
            for condition_id, severity, trigger, impact in rows
        ],
    }


def approval_checklist() -> Dict[str, Any]:
    rows = [
        "customer written approval captured",
        "security approval captured",
        "access window scheduled",
        "APP account verified",
        "DB account verified",
        "command catalog approved",
        "evidence storage approved",
        "stop conditions acknowledged",
        "no sudo boundary accepted",
        "no DB mutation boundary accepted",
        "no deployment boundary accepted",
    ]
    return {
        **common(),
        "section": "approval checklist",
        "items": [
            {
                "checkId": f"approval-{index:02d}",
                "title": title,
                "status": "pending" if index <= 8 else "not_captured",
                "executedInR3": False,
                "requiredBeforeActualObservation": True,
            }
            for index, title in enumerate(rows, start=1)
        ],
    }


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}


def summary() -> Dict[str, Any]:
    refs = source_references()
    app_commands = app_server_observation()["plannedCommands"]
    db_commands = db_server_observation()["plannedCommands"]
    return {
        **common(),
        "appServerIp": APP_SERVER_IP,
        "dbServerIp": DB_SERVER_IP,
        "observationStatus": "PLANNING_ONLY",
        "executionSequenceCount": len(execution_sequence()["items"]),
        "appObservationCommandCount": len(app_commands),
        "dbObservationCommandCount": len(db_commands),
        "evidencePackageItemCount": len(evidence_package()["items"]),
        "stopConditionCount": len(stop_conditions()["items"]),
        "approvalChecklistCount": len(approval_checklist()["items"]),
        "readyForActualSSH": False,
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
        "observationStatus": "PLANNING_ONLY",
        "serverReachability": "not_checked",
        "sshStatus": "not_executed",
        "runtimeHealthcheck": "not_executed",
        "limitations": data["limitations"],
    }
