#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14f/server-precheck-r14f.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14f/server-precheck-r14f.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14f/server-precheck-r14f.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r14f/server-precheck-r14f.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10.md", "ONE_SERVER_PRECHECK_R10_DEPLOYMENT_READINESS_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11.md", "ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12.md", "ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13.md", "ONE_SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13F.md", "ONE_SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14.md", "ONE_SERVER_PRECHECK_R14_APP_DB_DEPLOYMENT_EXECUTION_APPROVAL_GATE_PASS"),
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
    "menuImplementationMutationPerformed",
    "productionConfigMutationPerformed",
]

REVIEW_TRUE_FIELDS = {
    "evidenceChainFinalReview": [
        "r1ToR9EvidenceChainReviewed",
        "r10DeploymentReadinessReviewed",
        "r11DbPreparationReviewed",
        "r12AppPreparationReviewed",
        "r13ConsoleRuntimeVerificationReviewed",
        "r13fConsoleFinalReviewReviewed",
        "r14ExecutionApprovalGateReviewed",
    ],
    "dbFinalApprovalReview": [
        "targetDbServerConfirmed",
        "postgresqlDirectionConfirmed",
        "migrationPlanApproved",
        "backupPlanApproved",
        "rollbackPlanApproved",
        "seedPlanReviewed",
        "dbCredentialRestrictedReferenceApproved",
        "dbOperatorAssigned",
        "stopConditionsApproved",
    ],
    "appFinalApprovalReview": [
        "targetAppServerConfirmed",
        "backendDeploymentPlanApproved",
        "frontendStaticArtifactPlanApproved",
        "nginxPlanApproved",
        "processManagerPlanApproved",
        "runtimeEnvRestrictedReferenceApproved",
        "appDbConnectionPlanApproved",
        "appOperatorAssigned",
        "stopConditionsApproved",
    ],
    "baseRuntimeInstallationFinalReview": [
        "osPackageInstallationPlanApproved",
        "postgresRuntimePlanApproved",
        "nginxRuntimePlanApproved",
        "nodeRuntimePlanApproved",
        "pythonRuntimePlanApproved",
        "pm2RuntimePlanApproved",
        "offlineInstallModeReviewed",
        "dockerAbsencePlanReviewed",
    ],
    "backupRollbackStopConditionFinalReview": [
        "preDeploymentBackupRequired",
        "backupOperatorAssigned",
        "rollbackOperatorAssigned",
        "rollbackDecisionOwnerAssigned",
        "restoreProcedureReviewed",
        "failureStopConditionsReviewed",
        "postDeploymentVerificationPlanned",
    ],
    "humanApprovalFinalReview": [
        "executionWindowApproved",
        "humanApproverAssigned",
        "dbOperatorAssigned",
        "appOperatorAssigned",
        "rollbackOwnerAssigned",
        "stopConditionsApproved",
        "postDeploymentVerificationPlanned",
    ],
}

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


def expect_true(obj, field):
    if obj.get(field) is not True:
        fail(f"{field} must be true")


def expect_false(obj, field):
    if obj.get(field) is not False:
        fail(f"{field} must be false")


def expect_ready_pass(obj, name):
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


def check_no_executable_steps(paths):
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang not in EXECUTABLE_LANGS:
                continue
            for pattern in FORBIDDEN_EXEC_PATTERNS:
                if re.search(pattern, body, flags=re.IGNORECASE):
                    fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server, runtime, APP, DB, frontend, backend, Nginx, PM2, or OS operation steps found")


def main():
    required_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R14F documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R14F PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R14F":
        fail("registry taskId is not SERVER-PRECHECK-R14F")
    if reg.get("stage") != "SERVER-PRECHECK-R14F":
        fail("registry stage is not SERVER-PRECHECK-R14F")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R14F",
        "deploymentExecutionApprovalReference": "SERVER-PRECHECK-R14",
        "consoleGaFinalReviewReference": "SERVER-PRECHECK-R13F",
        "consoleGaRuntimeVerificationReference": "SERVER-PRECHECK-R13",
        "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
        "dbDeploymentPreparationReference": "SERVER-PRECHECK-R11",
        "appDeploymentPreparationReference": "SERVER-PRECHECK-R12",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("R14F evidence references R14, R13F, R13, R10, R11, and R12")

    if evid.get("r14PreviousDecision") != "HOLD":
        fail("r14PreviousDecision must be HOLD")
    if evid.get("r13fRuntimeVerificationFinalDecision") != "GO":
        fail("r13fRuntimeVerificationFinalDecision must be GO")
    ok("R13F GO dependency and previous R14 HOLD decision are recorded")

    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("deployment, SSH, server connection, installation, build, DB, healthcheck, smoke, and mutation flags are false")

    for section, fields in REVIEW_TRUE_FIELDS.items():
        review = evid.get(section, {})
        for field in fields:
            expect_true(review, field)
        expect_ready_pass(review, section)
    ok("evidence chain, DB, APP, runtime, backup/rollback, and human approval final reviews are PASS")

    secret = evid.get("secretHandlingFinalReview", {})
    for field in [
        "productionSecretStoredInPublicPacket",
        "productionEnvStoredInPublicPacket",
        "databaseUrlStoredInPublicPacket",
        "serverCredentialStoredInPublicPacket",
    ]:
        expect_false(secret, field)
    expect_true(secret, "restrictedSecretReferenceOnly")
    expect_ready_pass(secret, "secretHandlingFinalReview")
    ok("secret and restricted evidence final review is PASS")

    decision = evid.get("deploymentExecutionFinalApprovalDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("deploymentExecutionFinalApprovalDecision must be HOLD / GO / NO-GO")
    if decision != "GO":
        fail("deploymentExecutionFinalApprovalDecision must be GO for R14 HOLD reevaluation closure")
    if evid.get("reviewer", {}).get("reviewStatus") != "ACCEPTED":
        fail("reviewer reviewStatus must be ACCEPTED")
    if evid.get("approver", {}).get("approvalStatus") != "GO":
        fail("approver approvalStatus must be GO")
    if final.get("r13fDependencyStatus") != "GO":
        fail("final r13fDependencyStatus must be GO")
    if final.get("r14HoldReevaluationStatus") != "COMPLETE":
        fail("final r14HoldReevaluationStatus must be COMPLETE")
    if final.get("deploymentExecutionFinalApprovalDecision") != "GO":
        fail("final deploymentExecutionFinalApprovalDecision must be GO")
    ok("R14 HOLD reevaluation and deploymentExecutionFinalApprovalDecision are GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R10/R11/R12/R13/R13F/R14 source markers exist")

    check_no_executable_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R14F Deployment Execution Approval Final Verification validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
