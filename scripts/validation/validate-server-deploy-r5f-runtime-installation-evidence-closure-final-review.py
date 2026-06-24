#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R5F_RUNTIME_INSTALLATION_EVIDENCE_CLOSURE_FINAL_REVIEW_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5F.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5F_RUNTIME_INSTALLATION_EVIDENCE_CLOSURE_FINAL_REVIEW.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5F_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5f/server-deploy-r5f.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5f/server-deploy-r5f.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5f/server-deploy-r5f.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5f/server-deploy-r5f.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md", "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2.md", "ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3.md", "ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R4.md", "ONE_SERVER_DEPLOY_R4_RUNTIME_INSTALLATION_MANUAL_EXECUTION_RECORD_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5.md", "ONE_SERVER_DEPLOY_R5_RUNTIME_INSTALLATION_EVIDENCE_REVIEW_AND_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md", "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"),
]

FALSE_FLAGS = [
    "runtimeInstallationExecutedByThisPacket",
    "sshExecutedByThisPacket",
    "sshConnectionCommandStored",
    "realServerTargetStoredInPublicPacket",
    "serverCredentialStoredInPublicPacket",
    "appServerConnectionPerformedByThisPacket",
    "dbServerConnectionPerformedByThisPacket",
    "osPackageInstallationPerformedByThisPacket",
    "runtimeInstallationPerformedByThisPacket",
    "postgresInstallationPerformedByThisPacket",
    "nginxInstallationPerformedByThisPacket",
    "nodeNpmInstallationPerformedByThisPacket",
    "pythonPipInstallationPerformedByThisPacket",
    "pm2InstallationPerformedByThisPacket",
    "buildPerformedByThisPacket",
    "installPerformedByThisPacket",
    "restartReloadPerformedByThisPacket",
    "dbMigrationPerformedByThisPacket",
    "dbBackupPerformedByThisPacket",
    "dbRestorePerformedByThisPacket",
    "dbSeedPerformedByThisPacket",
    "dbUserCreatedByThisPacket",
    "dbPrivilegeMutationPerformedByThisPacket",
    "appToDbLiveConnectionTestPerformedByThisPacket",
    "healthcheckPerformedByThisPacket",
    "smokeTestPerformedByThisPacket",
    "serverMutationPerformedByThisPacket",
    "authMutationPerformedByThisPacket",
    "runtimeMutationPerformedByThisPacket",
    "frontendBackendMutationPerformedByThisPacket",
    "routeMutationPerformedByThisPacket",
    "menuImplementationMutationPerformedByThisPacket",
    "productionConfigMutationPerformedByThisPacket",
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
    ok("SERVER-DEPLOY-R5F documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R5F PASS marker exists in document, final review, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-DEPLOY-R5F":
        fail("registry taskId is not SERVER-DEPLOY-R5F")
    if evid.get("stage") != "SERVER-DEPLOY-R5F":
        fail("evidence stage is not SERVER-DEPLOY-R5F")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    expected_refs = {
        "runtimeInstallationPlanReference": "SERVER-DEPLOY-R1",
        "runtimeInstallationExecutionPacketReference": "SERVER-DEPLOY-R2",
        "runtimeInstallationManualApprovalReference": "SERVER-DEPLOY-R3",
        "runtimeInstallationManualExecutionRecordReference": "SERVER-DEPLOY-R4",
        "runtimeInstallationEvidenceGateReference": "SERVER-DEPLOY-R5",
        "precheckFinalApprovalReference": "SERVER-PRECHECK-R14F",
        "r4DecisionBeforeFinalReview": "HOLD",
        "r5DecisionBeforeFinalReview": "HOLD",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("R1/R2/R3/R4/R5/R14F references and pre-review HOLD decisions are recorded")

    expect_true(evid, "evidenceClosureOnly")
    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("evidence closure is true and execution, connection, installation, command, credential, and mutation flags are false")

    closure = evid.get("r4HoldClosureFinalReview", {})
    if closure.get("r4HoldClosureStatusBeforeFinalReview") != "HOLD":
        fail("r4HoldClosureStatusBeforeFinalReview must be HOLD")
    for field in [
        "executionSessionGapClosed",
        "appRuntimeEvidenceGapClosed",
        "dbRuntimeEvidenceGapClosed",
        "runtimePresenceEvidenceGapClosed",
        "backupEvidenceGapClosed",
        "rollbackEvidenceGapClosed",
        "operatorRecordGapClosed",
        "postExecutionEvidenceReviewGapClosed",
    ]:
        expect_true(closure, field)
    expect_pass(closure, "r4HoldClosureFinalReview")

    runtime = evid.get("runtimeEvidenceFinalReview", {})
    for field in [
        "executionSessionEvidenceAccepted",
        "withinApprovedWindow",
        "appRuntimeEvidenceAccepted",
        "dbRuntimeEvidenceAccepted",
        "runtimePresenceEvidenceAccepted",
        "backupCheckpointEvidenceAccepted",
        "rollbackCheckpointEvidenceAccepted",
        "operatorRecordAccepted",
        "postExecutionEvidenceAccepted",
    ]:
        expect_true(runtime, field)
    expect_pass(runtime, "runtimeEvidenceFinalReview")
    ok("R4/R5 HOLD closure and runtime evidence final review are PASS")

    app = evid.get("appRuntimeFinalResult", {})
    for field in ["pythonRuntimeResult", "nodeRuntimeResult", "pm2RuntimeResult", "nginxRuntimeResult"]:
        if app.get(field) != "PASS":
            fail(f"appRuntimeFinalResult.{field} must be PASS")
    if app.get("appRuntimeOverallResult") not in ["PASS", "WARN"]:
        fail("appRuntimeOverallResult must be PASS or WARN")
    expect_pass(app, "appRuntimeFinalResult")

    db = evid.get("dbRuntimeFinalResult", {})
    expect_true(db, "postgresqlDirectionConfirmed")
    for field in ["postgresRuntimeResult", "dbToolingResult", "backupToolingResult", "restoreToolingResult"]:
        if db.get(field) != "PASS":
            fail(f"dbRuntimeFinalResult.{field} must be PASS")
    if db.get("dbRuntimeOverallResult") not in ["PASS", "WARN"]:
        fail("dbRuntimeOverallResult must be PASS or WARN")
    expect_pass(db, "dbRuntimeFinalResult")
    ok("APP and DB runtime final results are PASS")

    redaction = evid.get("redactionRestrictedEvidenceFinalReview", {})
    expect_true(redaction, "publicEvidenceContainsNoSecrets")
    for field in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
        "realSshTargetStoredInPublicPacket",
        "rawCommandOutputStoredInPublicPacket",
    ]:
        expect_false(redaction, field)
    expect_true(redaction, "restrictedSecretReferenceOnly")
    expect_true(redaction, "restrictedRawEvidenceReferencedOnly")
    expect_pass(redaction, "redactionRestrictedEvidenceFinalReview")

    stops = evid.get("stopConditionFinalReview", {})
    for field in [
        "wrongServerTargetDetected",
        "packageIntegrityFailureDetected",
        "backupCheckpointMissingDetected",
        "unauthorizedPrivilegeEscalationDetected",
        "secretLeakageDetected",
        "unexpectedMutationDetected",
        "operatorMissingDetected",
        "rollbackOwnerUnavailableDetected",
    ]:
        expect_false(stops, field)
    expect_pass(stops, "stopConditionFinalReview")
    ok("redaction/restricted evidence and stop condition final reviews are PASS")

    if evid.get("reviewer", {}).get("reviewStatus") != "ACCEPTED":
        fail("reviewer.reviewStatus must be ACCEPTED")
    if evid.get("approver", {}).get("approvalStatus") != "GO":
        fail("approver.approvalStatus must be GO")
    if evid.get("runtimeInstallationEvidenceFinalDecision") != "GO":
        fail("runtimeInstallationEvidenceFinalDecision must be GO")
    if final.get("r4R5HoldClosureStatus") != "COMPLETE":
        fail("final r4R5HoldClosureStatus must be COMPLETE")
    if final.get("runtimeInstallationEvidenceFinalDecision") != "GO":
        fail("final runtimeInstallationEvidenceFinalDecision must be GO")
    ok("reviewer accepted, approver GO, and runtimeInstallationEvidenceFinalDecision is GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R1/R2/R3/R4/R5 and SERVER-PRECHECK-R14F source markers exist")

    checked_paths = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL]
    check_no_real_targets(checked_paths)
    check_no_executable_steps(checked_paths)

    ok("SERVER-DEPLOY-R5F Runtime Installation Evidence Closure Final Review validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
