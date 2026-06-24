#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r12/server-precheck-r12.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r12/server-precheck-r12.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r12/server-precheck-r12.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r12/server-precheck-r12.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R1.md", "ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R2.md", "ONE_SERVER_PRECHECK_R2_READONLY_ACCESS_WINDOW_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R3.md", "ONE_SERVER_PRECHECK_R3_ACTUAL_READONLY_OBSERVATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md", "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5.md", "ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6.md", "ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R7.md", "ONE_SERVER_PRECHECK_R7_HUMAN_APPROVAL_RECORD_AND_OBSERVATION_WINDOW_LOCK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R8.md", "ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R9.md", "ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10.md", "ONE_SERVER_PRECHECK_R10_DEPLOYMENT_READINESS_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11.md", "ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
]

REQUIRED_PACK_FIELDS = [
    "packId",
    "stage",
    "deploymentReadinessGateReference",
    "dbDeploymentPreparationReference",
    "approvalReference",
    "actualObservationEvidenceReference",
    "appDeploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "appServerConnectionPerformed",
    "appServerCommandExecuted",
    "backendCommandExecuted",
    "frontendCommandExecuted",
    "nginxCommandExecuted",
    "pm2CommandExecuted",
    "gunicornCommandExecuted",
    "flaskCommandExecuted",
    "nodeNpmCommandExecuted",
    "buildPerformed",
    "installPerformed",
    "restartPerformed",
    "dbServerConnectionPerformed",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "dbSeedPerformed",
    "appToDbLiveConnectionTestPerformed",
    "serverMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "routeMutationPerformed",
    "productionConfigMutationPerformed",
    "targetAppServer",
    "backendPreparation",
    "frontendPreparation",
    "nginxPreparation",
    "processManagerPreparation",
    "runtimeEnvironmentPreparation",
    "appDbConnectionPreparation",
    "healthcheckSmokePreparation",
    "rollbackPreparation",
    "consoleGaVerificationDependency",
    "secretHandling",
    "reviewer",
    "approver",
    "preparationDecision",
    "notes",
]

FALSE_PACK_FLAGS = [
    "appDeploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "appServerConnectionPerformed",
    "appServerCommandExecuted",
    "backendCommandExecuted",
    "frontendCommandExecuted",
    "nginxCommandExecuted",
    "pm2CommandExecuted",
    "gunicornCommandExecuted",
    "flaskCommandExecuted",
    "nodeNpmCommandExecuted",
    "buildPerformed",
    "installPerformed",
    "restartPerformed",
    "dbServerConnectionPerformed",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "dbSeedPerformed",
    "appToDbLiveConnectionTestPerformed",
    "serverMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "routeMutationPerformed",
    "productionConfigMutationPerformed",
]

FALSE_BOUNDARIES = [
    "sshExecutionAllowed",
    "sshAutomationAllowed",
    "sshConnectionCommandIncluded",
    "executableScriptAllowed",
    "appServerConnectionAllowed",
    "appServerCommandExecutionAllowed",
    "backendCommandExecutionAllowed",
    "frontendCommandExecutionAllowed",
    "nginxCommandExecutionAllowed",
    "pm2CommandExecutionAllowed",
    "gunicornCommandExecutionAllowed",
    "flaskCommandExecutionAllowed",
    "nodeNpmCommandExecutionAllowed",
    "deploymentAllowed",
    "installAllowed",
    "buildExecutionAllowed",
    "restartAllowed",
    "appRuntimeMutationAllowed",
    "dbServerConnectionAllowed",
    "dbMigrationAllowed",
    "dbBackupExecutionAllowed",
    "dbRestoreExecutionAllowed",
    "dbSeedExecutionAllowed",
    "appToDbLiveConnectionTestAllowed",
    "appServerMutationAllowed",
    "dbServerMutationAllowed",
    "authMutationAllowed",
    "runtimeMutationAllowed",
    "frontendChanged",
    "backendChanged",
    "routesChanged",
    "productionConfigMutationAllowed",
    "productionCredentialPublicStorageAllowed",
    "actualAppDeploymentExecutionByThisPacketAllowed",
]

EXECUTABLE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal", "sql"}
FORBIDDEN_EXEC_PATTERNS = [
    r"(^|\s)ssh\s+\S+@",
    r"(^|\s)ssh\s+-i\b",
    r"(^|\s)scp\b",
    r"(^|\s)rsync\b",
    r"(^|\s)sudo\b",
    r"\bsystemctl\s+restart\b",
    r"\bsystemctl\s+reload\b",
    r"\bnginx\s+-s\s+reload\b",
    r"\bdocker\s+compose\s+up\b",
    r"\bnpm\s+run\s+dev\b",
    r"\bnpm\s+run\s+build\b",
    r"\bnpm\s+install\b",
    r"\bpm2\s+start\b",
    r"\bpm2\s+restart\b",
    r"\bpm2\s+reload\b",
    r"\bpython\s+app\.py\b",
    r"\bflask\s+run\b",
    r"\bgunicorn\b",
    r"\bnode\s+server\.js\b",
    r"\bprisma\s+migrate\b",
    r"(^|\s)psql\b",
    r"(^|\s)pg_dump\b",
    r"(^|\s)pg_restore\b",
    r"\bcurl\b.*\b(production|prod)\b.*\b(mutate|mutation|write|delete|post|put|patch|health)\b",
]


def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def ok(msg):
    print(f"[PASS] {msg}")


def read(path):
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path):
    try:
        return json.loads(read(path))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def fenced_blocks(text):
    blocks = []
    in_block = False
    lang = ""
    current = []
    for line in text.splitlines():
        if line.startswith("```"):
            if in_block:
                blocks.append((lang, "\n".join(current)))
                in_block = False
                lang = ""
                current = []
            else:
                in_block = True
                lang = line[3:].strip().split()[0].lower() if line[3:].strip() else ""
            continue
        if in_block:
            current.append(line)
    if in_block:
        fail("unterminated fenced block")
    return blocks


def check_no_executable_app_steps(paths):
    executable_scope = []
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang in EXECUTABLE_LANGS:
                executable_scope.append((path, body))
    for path, body in executable_scope:
        for pattern in FORBIDDEN_EXEC_PATTERNS:
            if re.search(pattern, body, flags=re.IGNORECASE):
                fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server, APP, frontend, backend, Nginx, PM2, or DB operation steps found in executable block scope")


def check_readiness(section, allowed, label):
    if not isinstance(section, dict):
        fail(f"{label} must be an object")
    if section.get("readinessStatus") not in allowed:
        fail(f"{label} readinessStatus is invalid")


def main():
    required_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R12 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R12 PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R12":
        fail("registry taskId is not SERVER-PRECHECK-R12")
    if reg.get("mode") != "app-server-deployment-preparation-pack-only":
        fail("registry mode is not app-server-deployment-preparation-pack-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R12",
        "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
        "dbDeploymentPreparationReference": "SERVER-PRECHECK-R11",
        "approvalReference": "SERVER-PRECHECK-R7",
        "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and R10/R11/R7/R9 references are correct")

    for field in REQUIRED_PACK_FIELDS:
        if field not in evid:
            fail(f"required pack field missing: {field}")
        if field not in reg.get("requiredPackFields", []):
            fail(f"required pack field missing from registry: {field}")
    ok("required APP preparation pack fields are present")

    for key in FALSE_PACK_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    ok("APP deployment, SSH, connection, command, build, install, restart, DB, live test, and mutation flags are false")

    allowed_readiness = reg.get("allowedReadinessStatuses", [])
    for key in [
        "backendPreparation",
        "frontendPreparation",
        "nginxPreparation",
        "processManagerPreparation",
        "runtimeEnvironmentPreparation",
        "appDbConnectionPreparation",
        "healthcheckSmokePreparation",
        "rollbackPreparation",
        "consoleGaVerificationDependency",
        "secretHandling",
    ]:
        check_readiness(evid.get(key), allowed_readiness, key)

    frontend = evid.get("frontendPreparation", {})
    if frontend.get("buildExecutionAllowedByThisPacket") is not False:
        fail("buildExecutionAllowedByThisPacket must be false")
    nginx = evid.get("nginxPreparation", {})
    if nginx.get("nginxConfigMutationAllowedByThisPacket") is not False:
        fail("nginxConfigMutationAllowedByThisPacket must be false")
    process = evid.get("processManagerPreparation", {})
    if process.get("processCommandExecutionAllowedByThisPacket") is not False:
        fail("processCommandExecutionAllowedByThisPacket must be false")
    runtime_env = evid.get("runtimeEnvironmentPreparation", {})
    if runtime_env.get("productionEnvStoredInPublicPacket") is not False:
        fail("runtimeEnvironmentPreparation.productionEnvStoredInPublicPacket must be false")
    if runtime_env.get("restrictedEnvReferenceOnly") is not True:
        fail("restrictedEnvReferenceOnly must be true")
    ok("frontend, Nginx, process manager, and runtime environment constraints are correct")

    app_db = evid.get("appDbConnectionPreparation", {})
    if app_db.get("dependsOnR11") is not True:
        fail("dependsOnR11 must be true")
    if app_db.get("databaseUrlStoredInPublicPacket") is not False:
        fail("appDbConnectionPreparation.databaseUrlStoredInPublicPacket must be false")
    if app_db.get("restrictedCredentialReferenceOnly") is not True:
        fail("restrictedCredentialReferenceOnly must be true")
    if app_db.get("liveConnectionTestAllowedByThisPacket") is not False:
        fail("liveConnectionTestAllowedByThisPacket must be false")
    ok("APP-to-DB dependency on R11 and credential restrictions are correct")

    health = evid.get("healthcheckSmokePreparation", {})
    if health.get("healthcheckExecutionAllowedByThisPacket") is not False:
        fail("healthcheckExecutionAllowedByThisPacket must be false")
    if health.get("smokeExecutionAllowedByThisPacket") is not False:
        fail("smokeExecutionAllowedByThisPacket must be false")
    rollback = evid.get("rollbackPreparation", {})
    if rollback.get("rollbackPlanRequired") is not True:
        fail("rollbackPlanRequired must be true")
    if rollback.get("rollbackExecutionAllowedByThisPacket") is not False:
        fail("rollbackExecutionAllowedByThisPacket must be false")
    ok("healthcheck, smoke, and rollback constraints are correct")

    console = evid.get("consoleGaVerificationDependency", {})
    if console.get("required") is not True:
        fail("consoleGaVerificationDependency.required must be true")
    if console.get("plannedStage") != "SERVER-PRECHECK-R13":
        fail("consoleGaVerificationDependency.plannedStage must be SERVER-PRECHECK-R13")
    if console.get("menuArchitectureBaselineReference") != "MENU-GA-R1/R2":
        fail("menuArchitectureBaselineReference must be MENU-GA-R1/R2")
    ok("Console International GA verification dependency is correct")

    secret = evid.get("secretHandling", {})
    for key in [
        "productionAppSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "jwtSecretStoredInPublicPacket",
        "apiKeyStoredInPublicPacket",
    ]:
        if secret.get(key) is not False:
            fail(f"secretHandling.{key} must be false")
    if secret.get("restrictedSecretReferenceOnly") is not True:
        fail("restrictedSecretReferenceOnly must be true")
    ok("secret handling requirements are correct")

    reviewer_status = evid.get("reviewer", {}).get("reviewStatus")
    approver_status = evid.get("approver", {}).get("approvalStatus")
    if reviewer_status not in reg.get("allowedReviewStatuses", []):
        fail("reviewer reviewStatus is invalid")
    if approver_status not in reg.get("allowedApprovalStatuses", []):
        fail("approver approvalStatus is invalid")
    if evid.get("preparationDecision") not in reg.get("allowedPreparationDecisions", []):
        fail("preparationDecision must be HOLD / GO / NO-GO")
    ok("reviewer, approver, and preparation decision models are correct")

    boundaries = reg.get("boundaries", {})
    for key in FALSE_BOUNDARIES:
        if boundaries.get(key) is not False:
            fail(f"registry boundary must be false: {key}")
    final_boundaries = final.get("boundaries", {})
    for key, value in final_boundaries.items():
        if value is not False:
            fail(f"final verification boundary must be false: {key}")
    rules = reg.get("secretHandlingRules", {})
    for key in [
        "productionAppSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "jwtSecretStoredInPublicPacket",
        "apiKeyStoredInPublicPacket",
        "publicReleaseIndexIncludesRawSecretsOrProductionEnv",
    ]:
        if rules.get(key) is not False:
            fail(f"registry secretHandlingRules.{key} must be false")
    if rules.get("restrictedSecretReferenceOnly") is not True:
        fail("registry restrictedSecretReferenceOnly must be true")
    ok("registry and final verification boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R11 source markers exist")

    check_no_executable_app_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R12 APP Server Deployment Preparation Pack validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
