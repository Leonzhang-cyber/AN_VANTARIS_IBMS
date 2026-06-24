#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R14_APP_DB_DEPLOYMENT_EXECUTION_APPROVAL_GATE_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14.md"
GATE_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14_APP_DB_DEPLOYMENT_EXECUTION_APPROVAL_GATE.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14/server-precheck-r14.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14/server-precheck-r14.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14/server-precheck-r14.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14/server-precheck-r14.final-verification.json"
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
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12.md", "ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
]

FALSE_FLAGS = [
    "deploymentExecutionPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "appServerConnectionPerformed",
    "dbServerConnectionPerformed",
    "appServerCommandExecuted",
    "dbServerCommandExecuted",
    "osPackageInstallationPerformed",
    "runtimeInstallationPerformed",
    "postgresInstallationPerformed",
    "nginxInstallationPerformed",
    "nodeNpmInstallationPerformed",
    "pythonPipInstallationPerformed",
    "pm2InstallationPerformed",
    "buildPerformed",
    "installPerformed",
    "restartReloadPerformed",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "dbSeedPerformed",
    "dbUserCreated",
    "dbPrivilegeMutationPerformed",
    "appToDbLiveConnectionTestPerformed",
    "healthcheckPerformed",
    "smokeTestPerformed",
    "serverMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "routeMutationPerformed",
    "productionConfigMutationPerformed",
]

EXECUTABLE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal", "sql"}
FORBIDDEN_EXEC_PATTERNS = [
    r"(^|\s)ssh\s+\S+@",
    r"(^|\s)ssh\s+-i\b",
    r"(^|\s)scp\b",
    r"(^|\s)rsync\b",
    r"(^|\s)sudo\b",
    r"\bapt\s+install\b",
    r"\byum\s+install\b",
    r"\bdnf\s+install\b",
    r"\bsystemctl\s+start\b",
    r"\bsystemctl\s+restart\b",
    r"\bsystemctl\s+reload\b",
    r"\bnginx\s+-s\s+reload\b",
    r"\bdocker\s+compose\s+up\b",
    r"\bnpm\s+run\s+dev\b",
    r"\bnpm\s+run\s+build\b",
    r"\bnpm\s+install\b",
    r"\bpip\s+install\b",
    r"\bpm2\s+start\b",
    r"\bpm2\s+restart\b",
    r"\bpm2\s+reload\b",
    r"\bpython\s+app\.py\b",
    r"\bflask\s+run\b",
    r"\bgunicorn\b",
    r"\bnode\s+server\.js\b",
    r"\bprisma\s+migrate\b",
    r"(^|\s)psql\b",
    r"(^|\s)createdb\b",
    r"(^|\s)createuser\b",
    r"(^|\s)dropdb\b",
    r"(^|\s)pg_dump\b",
    r"(^|\s)pg_restore\b",
    r"\bALTER\s+USER\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bCREATE\s+DATABASE\b",
    r"\bDROP\s+DATABASE\b",
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


def check_no_executable_steps(paths):
    executable_scope = []
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang in EXECUTABLE_LANGS:
                executable_scope.append((path, body))
    for path, body in executable_scope:
        for pattern in FORBIDDEN_EXEC_PATTERNS:
            if re.search(pattern, body, flags=re.IGNORECASE):
                fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server, APP, DB, OS package, runtime, Nginx, PM2, healthcheck, or smoke operation steps found")


def check_readiness(section, allowed, label):
    if not isinstance(section, dict):
        fail(f"{label} must be an object")
    if section.get("readinessStatus") not in allowed:
        fail(f"{label}.readinessStatus is invalid")


def main():
    required_files = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R14 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R14 PASS marker exists in document, gate, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R14":
        fail("registry taskId is not SERVER-PRECHECK-R14")
    if reg.get("mode") != "app-db-deployment-execution-approval-gate-only":
        fail("registry mode is not app-db-deployment-execution-approval-gate-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R14",
        "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
        "dbDeploymentPreparationReference": "SERVER-PRECHECK-R11",
        "appDeploymentPreparationReference": "SERVER-PRECHECK-R12",
        "consoleGaRuntimeVerificationReference": "SERVER-PRECHECK-R13",
        "approvalReference": "SERVER-PRECHECK-R7",
        "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and R10/R11/R12/R13/R7/R9 references are correct")

    if evid.get("r13RequiredBeforeGo") is not True:
        fail("r13RequiredBeforeGo must be true")
    if evid.get("r13Completed") is not False:
        fail("r13Completed must be false until SERVER-PRECHECK-R13 exists")
    if evid.get("deploymentExecutionApprovalDecision") != "HOLD":
        fail("deploymentExecutionApprovalDecision must be HOLD when r13Completed is false")
    ok("R13 dependency HOLD rule is enforced")

    for key in FALSE_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    ok("deployment, SSH, connection, command, install, build, reload, DB, healthcheck, smoke, and mutation flags are false")

    allowed_readiness = reg.get("allowedReadinessStatuses", [])
    for key in [
        "evidenceChainReadiness",
        "dbExecutionApprovalInputs",
        "appExecutionApprovalInputs",
        "baseRuntimeInstallationApprovalInputs",
        "backupRollbackRecoveryApprovalInputs",
        "secretHandling",
        "executionApproval",
    ]:
        check_readiness(evid.get(key), allowed_readiness, key)

    if evid.get("dbExecutionApprovalInputs", {}).get("postgresqlDirectionConfirmed") is not True:
        fail("postgresqlDirectionConfirmed must be true")
    if evid.get("backupRollbackRecoveryApprovalInputs", {}).get("preDeploymentBackupRequired") is not True:
        fail("preDeploymentBackupRequired must be true")
    ok("PostgreSQL direction and pre-deployment backup requirement are correct")

    secret = evid.get("secretHandling", {})
    for key in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
    ]:
        if secret.get(key) is not False:
            fail(f"secretHandling.{key} must be false")
    if secret.get("restrictedSecretReferenceOnly") is not True:
        fail("restrictedSecretReferenceOnly must be true")
    ok("secret handling requirements are correct")

    if evid.get("reviewer", {}).get("reviewStatus") not in reg.get("allowedReviewStatuses", []):
        fail("reviewer reviewStatus is invalid")
    if evid.get("approver", {}).get("approvalStatus") not in reg.get("allowedApproverStatuses", []):
        fail("approver approvalStatus is invalid")
    if evid.get("deploymentExecutionApprovalDecision") not in reg.get("allowedApprovalDecisions", []):
        fail("deploymentExecutionApprovalDecision must be HOLD / GO / NO-GO")
    ok("reviewer, approver, and deployment execution approval decision models are correct")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    for key, value in final.get("boundaries", {}).items():
        if value is not False:
            fail(f"final verification boundary must be false: {key}")
    rules = reg.get("secretHandlingRules", {})
    for key in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
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
    ok("R1-R12 source markers exist; R13 is recorded as required and missing")

    check_no_executable_steps([DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R14 APP/DB Deployment Execution Approval Gate validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
