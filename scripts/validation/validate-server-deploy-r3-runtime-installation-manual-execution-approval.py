#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r3/server-deploy-r3.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r3/server-deploy-r3.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r3/server-deploy-r3.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r3/server-deploy-r3.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md", "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2.md", "ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md", "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"),
]

FALSE_FLAGS = [
    "runtimeInstallationExecutionAllowedByThisPacket",
    "automaticExecutionAllowed",
    "sshExecutedByThisPacket",
    "sshConnectionCommandStored",
    "realServerTargetStoredInPublicPacket",
    "serverCredentialStoredInPublicPacket",
    "appServerConnectionPerformed",
    "dbServerConnectionPerformed",
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
    "menuImplementationMutationPerformed",
    "productionConfigMutationPerformed",
]

EXECUTABLE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal", "sql"}
FORBIDDEN_REAL_EXEC_PATTERNS = [
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
REAL_TARGET_PATTERNS = [
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    r"\bssh\s+[A-Za-z0-9._-]+@[A-Za-z0-9._-]+\b",
    r"\b(?:password|token|secret|private[_ -]?key)\s*[:=]\s*[^<\s][^\n]+",
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


def expect_true(obj, field):
    if obj.get(field) is not True:
        fail(f"{field} must be true")


def expect_false(obj, field):
    if obj.get(field) is not False:
        fail(f"{field} must be false")


def expect_pass(obj, name):
    if obj.get("readinessStatus") != "PASS":
        fail(f"{name}.readinessStatus must be PASS")


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


def check_no_real_targets(paths):
    for path in paths:
        text = read(path)
        for pattern in REAL_TARGET_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"real target or credential-like value found in {path.relative_to(ROOT)}: {pattern}")
    ok("no real host, IP, email, SSH target, or credential assignment patterns found")


def check_no_executable_steps(paths):
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang not in EXECUTABLE_LANGS:
                continue
            for pattern in FORBIDDEN_REAL_EXEC_PATTERNS:
                if re.search(pattern, body, flags=re.IGNORECASE):
                    fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server, runtime, APP, DB, frontend, backend, Nginx, PM2, or OS operation steps found")


def main():
    required_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R3 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R3 PASS marker exists in document, approval packet, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-DEPLOY-R3":
        fail("registry taskId is not SERVER-DEPLOY-R3")
    if evid.get("stage") != "SERVER-DEPLOY-R3":
        fail("evidence stage is not SERVER-DEPLOY-R3")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    expected_refs = {
        "runtimeInstallationPlanReference": "SERVER-DEPLOY-R1",
        "runtimeInstallationExecutionPacketReference": "SERVER-DEPLOY-R2",
        "precheckFinalApprovalReference": "SERVER-PRECHECK-R14F",
        "runtimeInstallationPlanDecision": "GO",
        "runtimeInstallationExecutionPacketDecision": "GO",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("R1 GO, R2 GO, and R14F references are recorded")

    expect_true(evid, "manualExecutionApprovalOnly")
    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("manual approval is true and execution, connection, installation, command, credential, and mutation flags are false")

    window = evid.get("executionWindow", {})
    for field in [
        "windowDefined",
        "changeFreezeReviewed",
        "operatorAvailabilityReviewed",
        "rollbackOwnerAvailabilityReviewed",
        "evidenceReviewerAvailabilityReviewed",
    ]:
        expect_true(window, field)
    if window.get("timezone") != "Asia/Singapore":
        fail("executionWindow.timezone must be Asia/Singapore")
    for field in ["windowReference", "startTimeReference", "endTimeReference"]:
        value = window.get(field, "")
        if not isinstance(value, str) or not value.startswith("RESTRICTED_"):
            fail(f"executionWindow.{field} must be a restricted reference")
    expect_pass(window, "executionWindow")
    ok("execution window requirements are PASS")

    operators = evid.get("operatorAssignment", {})
    for field in [
        "humanApproverAssigned",
        "executionCoordinatorAssigned",
        "appOperatorAssigned",
        "dbOperatorAssigned",
        "rollbackOwnerAssigned",
        "evidenceReviewerAssigned",
    ]:
        expect_true(operators, field)
    expect_pass(operators, "operatorAssignment")
    ok("operator assignment requirements are PASS")

    app = evid.get("appRuntimeManualApproval", {})
    for field in [
        "pythonRuntimeInstallApproved",
        "nodeRuntimeInstallApproved",
        "pm2RuntimeInstallApproved",
        "nginxRuntimeInstallApproved",
        "appServerTargetReferenceApproved",
        "realTargetRedactionRequired",
    ]:
        expect_true(app, field)
    expect_pass(app, "appRuntimeManualApproval")
    ok("APP runtime manual approval is PASS")

    db = evid.get("dbRuntimeManualApproval", {})
    for field in [
        "postgresRuntimeInstallApproved",
        "postgresqlDirectionConfirmed",
        "dbToolingApproved",
        "backupRestoreToolingApproved",
        "dbServerTargetReferenceApproved",
        "dbUserPrivilegeMutationExcludedFromThisApproval",
        "realTargetRedactionRequired",
    ]:
        expect_true(db, field)
    expect_pass(db, "dbRuntimeManualApproval")
    ok("DB runtime manual approval is PASS and PostgreSQL direction is confirmed")

    offline = evid.get("offlineNoDockerManualApproval", {})
    expect_false(offline, "dockerRequired")
    for field in ["noDockerPathApproved", "offlineModeApproved", "offlinePackageInventoryApproved", "offlineBundleIntegrityCheckApproved"]:
        expect_true(offline, field)
    expect_pass(offline, "offlineNoDockerManualApproval")
    ok("offline/no-Docker manual approval is PASS")

    backup = evid.get("backupCheckpointApproval", {})
    for field in [
        "backupRequiredBeforeInstallation",
        "backupCheckpointApproved",
        "backupOperatorAssigned",
        "backupExecutionExcludedFromThisPacket",
        "backupEvidenceRequiredAfterExecution",
    ]:
        expect_true(backup, field)
    expect_pass(backup, "backupCheckpointApproval")

    rollback = evid.get("rollbackCheckpointApproval", {})
    for field in ["rollbackPlanRequired", "rollbackCheckpointApproved", "rollbackOwnerAssigned", "rollbackExecutionExcludedFromThisPacket"]:
        expect_true(rollback, field)
    expect_pass(rollback, "rollbackCheckpointApproval")
    ok("backup and rollback checkpoint approvals are PASS without execution")

    stops = evid.get("stopConditionApproval", {})
    for field in [
        "stopConditionsRequired",
        "stopOnSecretLeakage",
        "stopOnUnexpectedMutation",
        "stopOnWrongServerTarget",
        "stopOnPackageIntegrityFailure",
        "stopOnBackupCheckpointMissing",
        "stopOnUnauthorizedPrivilegeEscalation",
        "stopOnOperatorMissing",
        "stopOnRollbackOwnerUnavailable",
        "stopConditionsApproved",
    ]:
        expect_true(stops, field)
    expect_pass(stops, "stopConditionApproval")
    ok("stop condition approval is PASS")

    post = evid.get("postInstallEvidenceApproval", {})
    for field in [
        "postInstallEvidenceRequired",
        "redactedEvidenceRequired",
        "restrictedEvidenceReferenceOnly",
        "runtimePresenceEvidenceRequired",
        "serviceStatusEvidenceRequired",
        "packageVersionEvidenceRequired",
        "backupCheckpointEvidenceRequired",
        "rollbackCheckpointEvidenceRequired",
        "operatorExecutionRecordRequired",
    ]:
        expect_true(post, field)
    expect_false(post, "rawEvidenceStoredInPublicPacket")
    expect_pass(post, "postInstallEvidenceApproval")
    ok("post-install evidence approval is PASS")

    secret = evid.get("secretHandling", {})
    for field in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
        "realSshTargetStoredInPublicPacket",
    ]:
        expect_false(secret, field)
    expect_true(secret, "restrictedSecretReferenceOnly")
    expect_pass(secret, "secretHandling")
    ok("secret handling is PASS")

    decision = evid.get("runtimeInstallationManualApprovalDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeInstallationManualApprovalDecision must be HOLD / GO / NO-GO")
    if decision != "GO":
        fail("runtimeInstallationManualApprovalDecision must be GO for R3 completion")
    if final.get("r2DependencyStatus") != "GO":
        fail("final r2DependencyStatus must be GO")
    if final.get("manualExecutionApprovalOnly") is not True:
        fail("final manualExecutionApprovalOnly must be true")
    if final.get("automaticExecutionAllowed") is not False:
        fail("final automaticExecutionAllowed must be false")
    if final.get("runtimeInstallationManualApprovalDecision") != "GO":
        fail("final runtimeInstallationManualApprovalDecision must be GO")
    ok("runtimeInstallationManualApprovalDecision is GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R1/R2 and SERVER-PRECHECK-R14F source markers exist")

    checked_paths = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL]
    check_no_real_targets(checked_paths)
    check_no_executable_steps(checked_paths)

    ok("SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
