#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET.md"
COMMAND_REVIEW = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2_MANUAL_COMMAND_REVIEW_PACKET.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r2/server-deploy-r2.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r2/server-deploy-r2.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r2/server-deploy-r2.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r2/server-deploy-r2.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md", "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md", "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"),
]

FALSE_FLAGS = [
    "runtimeInstallationExecutionAllowedByThisPacket",
    "automaticExecutionAllowed",
    "sshExecutedByThisPacket",
    "sshConnectionCommandStored",
    "realServerTargetStoredInPublicPacket",
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
    required_files = [DOC, PACK_DOC, COMMAND_REVIEW, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R2 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, COMMAND_REVIEW, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R2 PASS marker exists in document, packet, command review, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-DEPLOY-R2":
        fail("registry taskId is not SERVER-DEPLOY-R2")
    if evid.get("stage") != "SERVER-DEPLOY-R2":
        fail("evidence stage is not SERVER-DEPLOY-R2")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    if evid.get("runtimeInstallationPlanReference") != "SERVER-DEPLOY-R1":
        fail("runtimeInstallationPlanReference must be SERVER-DEPLOY-R1")
    if evid.get("precheckFinalApprovalReference") != "SERVER-PRECHECK-R14F":
        fail("precheckFinalApprovalReference must be SERVER-PRECHECK-R14F")
    if evid.get("runtimeInstallationPlanDecision") != "GO":
        fail("runtimeInstallationPlanDecision must be GO")
    ok("R1 GO and R14F references are recorded")

    expect_true(evid, "manualCommandReviewOnly")
    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("manual review is true and execution, connection, installation, command, evidence, and mutation flags are false")

    app = evid.get("appRuntimeExecutionSequence", {})
    for field in [
        "pythonRuntimeStepReviewed",
        "nodeRuntimeStepReviewed",
        "pm2RuntimeStepReviewed",
        "nginxRuntimeStepReviewed",
        "packageSourceReviewed",
        "offlineBundleReviewed",
        "rollbackCheckpointReviewed",
        "stopConditionCheckpointReviewed",
        "executionCommandsStoredAsTemplatesOnly",
        "realTargetsRedacted",
    ]:
        expect_true(app, field)
    expect_false(app, "executionAllowedByThisPacket")
    expect_pass(app, "appRuntimeExecutionSequence")
    ok("APP runtime execution sequence is PASS and template-only")

    db = evid.get("dbRuntimeExecutionSequence", {})
    for field in [
        "postgresRuntimeStepReviewed",
        "postgresVersionPlanReviewed",
        "dbToolingReviewed",
        "backupToolingStepReviewed",
        "restoreToolingStepReviewed",
        "packageSourceReviewed",
        "offlineBundleReviewed",
        "rollbackCheckpointReviewed",
        "stopConditionCheckpointReviewed",
        "executionCommandsStoredAsTemplatesOnly",
        "realTargetsRedacted",
    ]:
        expect_true(db, field)
    expect_false(db, "executionAllowedByThisPacket")
    expect_pass(db, "dbRuntimeExecutionSequence")
    ok("DB runtime execution sequence is PASS and template-only")

    offline = evid.get("offlineNoDockerExecutionPath", {})
    expect_false(offline, "dockerRequired")
    for field in ["offlineModeSupported", "noDockerPathReviewed", "offlinePackageInventoryReviewed", "offlineBundleIntegrityCheckPlanned", "onlinePackageSourceFallbackReviewed"]:
        expect_true(offline, field)
    expect_false(offline, "executionAllowedByThisPacket")
    expect_pass(offline, "offlineNoDockerExecutionPath")
    ok("offline/no-Docker execution path is PASS")

    backup = evid.get("preInstallBackupCheckpoint", {})
    for field in ["backupRequiredBeforeInstallation", "backupCheckpointDefined", "backupEvidenceRequiredAfterExecution"]:
        expect_true(backup, field)
    expect_false(backup, "backupExecutionAllowedByThisPacket")
    expect_pass(backup, "preInstallBackupCheckpoint")

    rollback = evid.get("rollbackCheckpoint", {})
    for field in ["rollbackPlanRequired", "rollbackCheckpointDefined", "rollbackOwnerRequired"]:
        expect_true(rollback, field)
    expect_false(rollback, "rollbackExecutionAllowedByThisPacket")
    expect_pass(rollback, "rollbackCheckpoint")
    ok("backup and rollback checkpoints are PASS without execution")

    stops = evid.get("stopConditions", {})
    for field in [
        "stopConditionsRequired",
        "stopOnSecretLeakage",
        "stopOnUnexpectedMutation",
        "stopOnWrongServerTarget",
        "stopOnPackageIntegrityFailure",
        "stopOnBackupCheckpointMissing",
        "stopOnUnapprovedPrivilegeEscalation",
        "stopOnOperatorMissing",
        "stopConditionsReviewed",
    ]:
        expect_true(stops, field)
    expect_pass(stops, "stopConditions")
    ok("stop conditions are PASS")

    operator = evid.get("operatorApproval", {})
    for field in ["executionWindowDefined", "humanApproverAssigned", "appOperatorAssigned", "dbOperatorAssigned", "rollbackOwnerAssigned", "manualExecutionRequired"]:
        expect_true(operator, field)
    expect_pass(operator, "operatorApproval")

    post = evid.get("postInstallEvidenceFormat", {})
    for field in ["postInstallEvidenceRequired", "redactedEvidenceRequired", "restrictedEvidenceReferenceOnly", "healthcheckEvidencePlannedForLaterStage", "smokeEvidencePlannedForLaterStage"]:
        expect_true(post, field)
    expect_false(post, "rawEvidenceStoredInPublicPacket")
    expect_pass(post, "postInstallEvidenceFormat")
    ok("operator approval and post-install evidence format are PASS")

    secret = evid.get("secretHandling", {})
    for field in ["productionSecretStoredInPublicPacket", "productionEnvStoredInPublicPacket", "databaseUrlStoredInPublicPacket", "serverCredentialStoredInPublicPacket"]:
        expect_false(secret, field)
    expect_true(secret, "restrictedSecretReferenceOnly")
    expect_pass(secret, "secretHandling")
    ok("secret handling is PASS")

    decision = evid.get("runtimeInstallationExecutionPacketDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeInstallationExecutionPacketDecision must be HOLD / GO / NO-GO")
    if decision != "GO":
        fail("runtimeInstallationExecutionPacketDecision must be GO for R2 completion")
    if final.get("r1DependencyStatus") != "GO":
        fail("final r1DependencyStatus must be GO")
    if final.get("manualCommandReviewOnly") is not True:
        fail("final manualCommandReviewOnly must be true")
    if final.get("automaticExecutionAllowed") is not False:
        fail("final automaticExecutionAllowed must be false")
    if final.get("runtimeInstallationExecutionPacketDecision") != "GO":
        fail("final runtimeInstallationExecutionPacketDecision must be GO")
    ok("runtimeInstallationExecutionPacketDecision is GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R1 and SERVER-PRECHECK-R14F source markers exist")

    checked_paths = [DOC, PACK_DOC, COMMAND_REVIEW, FINAL_NOTE, REG, EVID, VAL, FINAL]
    check_no_real_targets(checked_paths)
    check_no_executable_steps(checked_paths)

    ok("SERVER-DEPLOY-R2 Runtime Installation Execution Packet validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
