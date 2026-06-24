#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R6_DB_DEPLOYMENT_PREPARATION_EXECUTION_GATE_PASS"
R5F_PASS = "ONE_SERVER_DEPLOY_R5F_RUNTIME_INSTALLATION_EVIDENCE_CLOSURE_FINAL_REVIEW_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R6.md"
GATE_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R6_DB_DEPLOYMENT_PREPARATION_EXECUTION_GATE.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R6_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r6/server-deploy-r6.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r6/server-deploy-r6.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r6/server-deploy-r6.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r6/server-deploy-r6.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"
R5F_EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r5f/server-deploy-r5f.evidence.json"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md", "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R2.md", "ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R3.md", "ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R4.md", "ONE_SERVER_DEPLOY_R4_RUNTIME_INSTALLATION_MANUAL_EXECUTION_RECORD_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5.md", "ONE_SERVER_DEPLOY_R5_RUNTIME_INSTALLATION_EVIDENCE_REVIEW_AND_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R5F.md", R5F_PASS),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md", "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"),
]

FALSE_FLAGS = [
    "dbDeploymentExecutionAllowedByThisPacket",
    "sshExecutedByThisPacket",
    "sshConnectionCommandStored",
    "realServerTargetStoredInPublicPacket",
    "serverCredentialStoredInPublicPacket",
    "dbServerConnectionPerformedByThisPacket",
    "appServerConnectionPerformedByThisPacket",
    "postgresCommandExecutedByThisPacket",
    "psqlExecutedByThisPacket",
    "dbDeploymentPerformedByThisPacket",
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
    "dbMutationPerformedByThisPacket",
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


def expect_status(obj, name, status):
    if obj.get("readinessStatus") != status:
        fail(f"{name}.readinessStatus must be {status}")


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
    ok("no executable server, DB, PostgreSQL, APP, frontend, backend, Nginx, PM2, OS package, or runtime operation steps found")


def main():
    required_files = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R6 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R6 PASS marker exists in document, gate record, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)
    r5f = load_json(R5F_EVID)

    if reg.get("taskId") != "SERVER-DEPLOY-R6":
        fail("registry taskId is not SERVER-DEPLOY-R6")
    if evid.get("stage") != "SERVER-DEPLOY-R6":
        fail("evidence stage is not SERVER-DEPLOY-R6")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    if reg.get("passMarker") != PASS or evid.get("passMarker") != PASS:
        fail("registry or evidence pass marker mismatch")
    ok("registry, evidence, validation, and final verification markers are correct")

    expected_refs = {
        "precheckFinalApprovalReference": "SERVER-PRECHECK-R14F",
        "runtimeInstallationPlanReference": "SERVER-DEPLOY-R1",
        "runtimeInstallationExecutionPacketReference": "SERVER-DEPLOY-R2",
        "runtimeInstallationManualApprovalReference": "SERVER-DEPLOY-R3",
        "runtimeInstallationManualExecutionRecordReference": "SERVER-DEPLOY-R4",
        "runtimeInstallationEvidenceGateReference": "SERVER-DEPLOY-R5",
        "runtimeInstallationEvidenceClosureReference": "SERVER-DEPLOY-R5F",
        "runtimeInstallationEvidenceFinalDecision": "GO",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    if r5f.get("runtimeInstallationEvidenceFinalDecision") != "GO":
        fail("R5F runtimeInstallationEvidenceFinalDecision must be GO")
    ok("R1/R2/R3/R4/R5/R5F/R14F references and R5F GO dependency are recorded")

    expect_true(evid, "dbDeploymentPreparationGateOnly")
    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("DB preparation gate is true and execution, connection, command, credential, mutation, and production-config flags are false")

    pg = evid.get("postgresRuntimeDependency", {})
    for field in [
        "postgresqlDirectionConfirmed",
        "postgresRuntimeEvidenceAccepted",
        "dbToolingEvidenceAccepted",
        "backupToolingEvidenceAccepted",
        "restoreToolingEvidenceAccepted",
    ]:
        expect_true(pg, field)
    if pg.get("postgresRuntimeEvidenceReference") != "SERVER-DEPLOY-R5F":
        fail("postgres runtime evidence reference must be SERVER-DEPLOY-R5F")
    expect_status(pg, "postgresRuntimeDependency", "PASS")
    ok("PostgreSQL runtime, DB tooling, backup tooling, and restore tooling evidence are accepted")

    mig = evid.get("dbMigrationExecutionReadiness", {})
    for field in [
        "migrationInventoryReviewed",
        "migrationOrderReviewed",
        "migrationRollbackImpactReviewed",
        "migrationOperatorAssigned",
        "migrationExecutionAllowedByThisPacket",
    ]:
        expect_false(mig, field)
    expect_true(mig, "migrationCommandsStoredAsTemplatesOnly")
    expect_true(mig, "realDbTargetRedacted")
    expect_status(mig, "dbMigrationExecutionReadiness", "HOLD")

    backup = evid.get("preMigrationBackupCheckpoint", {})
    expect_true(backup, "backupRequiredBeforeMigration")
    expect_false(backup, "backupCheckpointDefined")
    expect_false(backup, "backupOperatorAssigned")
    expect_true(backup, "backupEvidenceRequiredAfterExecution")
    expect_false(backup, "backupExecutionAllowedByThisPacket")
    expect_status(backup, "preMigrationBackupCheckpoint", "HOLD")

    rollback = evid.get("rollbackRestoreReadiness", {})
    expect_true(rollback, "rollbackPlanRequired")
    expect_false(rollback, "rollbackPlanReviewed")
    expect_false(rollback, "restoreProcedureReviewed")
    expect_false(rollback, "rollbackOwnerAssigned")
    expect_false(rollback, "restoreExecutionAllowedByThisPacket")
    expect_status(rollback, "rollbackRestoreReadiness", "HOLD")

    seed = evid.get("seedReadiness", {})
    expect_false(seed, "seedRequired")
    expect_false(seed, "seedInventoryReviewed")
    expect_false(seed, "seedSensitivityReviewed")
    expect_false(seed, "seedOperatorAssigned")
    expect_false(seed, "seedExecutionAllowedByThisPacket")
    expect_status(seed, "seedReadiness", "HOLD")

    privilege = evid.get("dbUserPrivilegeBoundary", {})
    expect_true(privilege, "dbUserCreationExcludedFromThisPacket")
    expect_true(privilege, "dbPrivilegeMutationExcludedFromThisPacket")
    expect_false(privilege, "leastPrivilegePlanReviewed")
    expect_false(privilege, "productionSuperuserCredentialStoredInPublicPacket")
    expect_status(privilege, "dbUserPrivilegeBoundary", "HOLD")

    app_db = evid.get("appDbConnectionPlanReview", {})
    expect_false(app_db, "appToDbConnectionPlanReviewed")
    expect_false(app_db, "liveConnectionTestAllowedByThisPacket")
    expect_false(app_db, "databaseUrlStoredInPublicPacket")
    expect_true(app_db, "restrictedCredentialReferenceOnly")
    expect_status(app_db, "appDbConnectionPlanReview", "HOLD")
    ok("migration, backup, rollback/restore, seed, privilege, and APP-to-DB readiness models are HOLD")

    secret = evid.get("secretHandling", {})
    for field in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "dbPasswordStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
        "realDbTargetStoredInPublicPacket",
    ]:
        expect_false(secret, field)
    expect_true(secret, "restrictedSecretReferenceOnly")
    expect_status(secret, "secretHandling", "PASS")
    ok("restricted DB credential handling is PASS and public secret fields are false")

    stop = evid.get("stopConditions", {})
    for field in [
        "stopConditionsRequired",
        "stopOnWrongDbTarget",
        "stopOnBackupCheckpointMissing",
        "stopOnMigrationOrderMismatch",
        "stopOnSecretLeakage",
        "stopOnUnexpectedDbMutation",
        "stopOnUnauthorizedPrivilegeEscalation",
        "stopOnMissingRollbackOwner",
    ]:
        expect_true(stop, field)
    expect_false(stop, "stopConditionsReviewed")
    expect_status(stop, "stopConditions", "HOLD")

    people = evid.get("operatorReviewerApprover", {})
    for field in [
        "dbOperatorAssigned",
        "migrationOperatorAssigned",
        "backupOperatorAssigned",
        "rollbackOwnerAssigned",
        "evidenceReviewerAssigned",
        "humanApproverAssigned",
    ]:
        expect_false(people, field)
    expect_status(people, "operatorReviewerApprover", "HOLD")
    ok("stop conditions and operator/reviewer/approver requirements are HOLD")

    if evid.get("reviewer", {}).get("reviewStatus") != "PENDING":
        fail("reviewer reviewStatus must be PENDING")
    if evid.get("approver", {}).get("approvalStatus") != "HOLD":
        fail("approver approvalStatus must be HOLD")
    if evid.get("dbDeploymentPreparationExecutionGateDecision") not in {"HOLD", "GO", "NO-GO"}:
        fail("dbDeploymentPreparationExecutionGateDecision must be HOLD, GO, or NO-GO")
    if evid.get("dbDeploymentPreparationExecutionGateDecision") != "HOLD":
        fail("R6 evidence decision must remain HOLD until required preparation is completed")
    if final.get("dbDeploymentPreparationExecutionGateDecision") != "HOLD":
        fail("final verification decision must be HOLD")
    ok("reviewer pending, approver HOLD, and dbDeploymentPreparationExecutionGateDecision is HOLD")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"source marker missing from {path.relative_to(ROOT)}")
    if R5F_PASS not in read(INDEX):
        fail("R5F PASS marker missing from release index")
    ok("SERVER-DEPLOY-R1/R2/R3/R4/R5/R5F and SERVER-PRECHECK-R14F source markers exist")

    scan_paths = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    check_no_real_targets(scan_paths)
    check_no_executable_steps(scan_paths)

    ok("SERVER-DEPLOY-R6 DB Deployment Preparation Execution Gate validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
