#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R5_RUNTIME_INSTALLATION_EVIDENCE_REVIEW_AND_GATE_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5_RUNTIME_INSTALLATION_EVIDENCE_REVIEW_AND_GATE.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5/server-deploy-r5.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5/server-deploy-r5.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5/server-deploy-r5.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5/server-deploy-r5.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md", "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2.md", "ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3.md", "ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R4.md", "ONE_SERVER_DEPLOY_R4_RUNTIME_INSTALLATION_MANUAL_EXECUTION_RECORD_PASS"),
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
    ok("SERVER-DEPLOY-R5 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R5 PASS marker exists in document, gate packet, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-DEPLOY-R5":
        fail("registry taskId is not SERVER-DEPLOY-R5")
    if evid.get("stage") != "SERVER-DEPLOY-R5":
        fail("evidence stage is not SERVER-DEPLOY-R5")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    expected_refs = {
        "runtimeInstallationPlanReference": "SERVER-DEPLOY-R1",
        "runtimeInstallationExecutionPacketReference": "SERVER-DEPLOY-R2",
        "runtimeInstallationManualApprovalReference": "SERVER-DEPLOY-R3",
        "runtimeInstallationManualExecutionRecordReference": "SERVER-DEPLOY-R4",
        "precheckFinalApprovalReference": "SERVER-PRECHECK-R14F",
        "runtimeInstallationPlanDecision": "GO",
        "runtimeInstallationExecutionPacketDecision": "GO",
        "runtimeInstallationManualApprovalDecision": "GO",
        "runtimeInstallationExecutionRecordDecisionBeforeReview": "HOLD",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("R1/R2/R3 GO, R4 HOLD, and R14F references are recorded")

    expect_true(evid, "evidenceReviewOnly")
    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("evidence review is true and execution, connection, installation, command, credential, and mutation flags are false")

    closure = evid.get("r4HoldClosureReview", {})
    if closure.get("r4DecisionBeforeReview") != "HOLD":
        fail("r4DecisionBeforeReview must be HOLD")
    expect_true(closure, "r4HoldReasonReviewed")
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
        expect_false(closure, field)
    if closure.get("readinessStatus") != "HOLD":
        fail("r4HoldClosureReview.readinessStatus must be HOLD")
    ok("R4 HOLD closure review remains HOLD with documented gaps")

    session = evid.get("executionSessionEvidenceReview", {})
    expect_false(session, "executionSessionRecorded")
    expect_false(session, "withinApprovedWindow")
    expect_true(session, "manualOperatorExecutedOutsideRepository")
    expect_false(session, "executionStatusAccepted")

    app = evid.get("appRuntimeEvidenceReview", {})
    if app.get("appRuntimeOverallResult") != "NOT_RECORDED":
        fail("appRuntimeOverallResult must be NOT_RECORDED")
    for field in ["pythonRuntimeResultReviewed", "nodeRuntimeResultReviewed", "pm2RuntimeResultReviewed", "nginxRuntimeResultReviewed", "appRawEvidenceStoredInPublicPacket"]:
        expect_false(app, field)
    expect_true(app, "appEvidenceRedacted")
    expect_true(app, "restrictedEvidenceReferenceOnly")

    db = evid.get("dbRuntimeEvidenceReview", {})
    expect_true(db, "postgresqlDirectionConfirmed")
    if db.get("dbRuntimeOverallResult") != "NOT_RECORDED":
        fail("dbRuntimeOverallResult must be NOT_RECORDED")
    for field in ["postgresRuntimeResultReviewed", "dbToolingResultReviewed", "backupToolingResultReviewed", "restoreToolingResultReviewed", "dbRawEvidenceStoredInPublicPacket"]:
        expect_false(db, field)
    expect_true(db, "dbEvidenceRedacted")
    expect_true(db, "restrictedEvidenceReferenceOnly")
    ok("execution, APP, and DB evidence reviews remain HOLD with safe evidence handling")

    runtime = evid.get("runtimePresenceEvidenceReview", {})
    for field in ["pythonPresenceEvidenceAccepted", "nodePresenceEvidenceAccepted", "pm2PresenceEvidenceAccepted", "nginxPresenceEvidenceAccepted", "postgresPresenceEvidenceAccepted", "runtimeRawEvidenceStoredInPublicPacket"]:
        expect_false(runtime, field)
    expect_true(runtime, "runtimeEvidenceRedacted")
    expect_true(runtime, "restrictedEvidenceReferenceOnly")

    backup = evid.get("backupCheckpointEvidenceReview", {})
    expect_true(backup, "backupRequiredBeforeInstallation")
    expect_false(backup, "backupCheckpointEvidenceAccepted")
    expect_true(backup, "backupEvidenceRedacted")
    expect_false(backup, "backupRawEvidenceStoredInPublicPacket")
    expect_true(backup, "restrictedEvidenceReferenceOnly")

    rollback = evid.get("rollbackCheckpointEvidenceReview", {})
    expect_true(rollback, "rollbackPlanRequired")
    expect_false(rollback, "rollbackCheckpointEvidenceAccepted")
    expect_false(rollback, "rollbackOwnerAccepted")
    expect_true(rollback, "rollbackEvidenceRedacted")
    expect_false(rollback, "rollbackRawEvidenceStoredInPublicPacket")
    expect_true(rollback, "restrictedEvidenceReferenceOnly")
    ok("runtime presence, backup, and rollback evidence reviews remain HOLD with public raw evidence blocked")

    stops = evid.get("stopConditionReview", {})
    expect_true(stops, "stopConditionsReviewed")
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
    ok("stop condition review is PASS")

    operator = evid.get("operatorReviewerApproverReview", {})
    for field in [
        "executionCoordinatorAccepted",
        "appOperatorAccepted",
        "dbOperatorAccepted",
        "backupOperatorAccepted",
        "rollbackOwnerAccepted",
        "evidenceReviewerAccepted",
        "humanApproverAccepted",
    ]:
        expect_false(operator, field)
    if operator.get("readinessStatus") != "HOLD":
        fail("operatorReviewerApproverReview.readinessStatus must be HOLD")

    redaction = evid.get("redactionRestrictedEvidenceReview", {})
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
    ok("operator review is HOLD and redaction/restricted evidence review is PASS")

    decision = evid.get("runtimeInstallationEvidenceGateDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeInstallationEvidenceGateDecision must be HOLD / GO / NO-GO")
    if decision != "HOLD":
        fail("runtimeInstallationEvidenceGateDecision must be HOLD while R4 evidence gaps remain open")
    if final.get("r4DependencyStatus") != "COMPLETE":
        fail("final r4DependencyStatus must be COMPLETE")
    if final.get("r4HoldClosureStatus") != "HOLD":
        fail("final r4HoldClosureStatus must be HOLD")
    if final.get("runtimeInstallationEvidenceGateDecision") != "HOLD":
        fail("final runtimeInstallationEvidenceGateDecision must be HOLD")
    ok("runtimeInstallationEvidenceGateDecision is HOLD")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R1/R2/R3/R4 and SERVER-PRECHECK-R14F source markers exist")

    checked_paths = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL]
    check_no_real_targets(checked_paths)
    check_no_executable_steps(checked_paths)

    ok("SERVER-DEPLOY-R5 Runtime Installation Evidence Review and Gate validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
