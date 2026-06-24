#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_DEPLOY_R1_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r1/server-deploy-r1.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r1/server-deploy-r1.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r1/server-deploy-r1.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-deploy-r1/server-deploy-r1.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/MENU_GA_R1.md", "ONE_MENU_GA_R1_INTERNATIONAL_L1_L2_L3_MENU_ARCHITECTURE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/MENU_GA_R2.md", "ONE_MENU_GA_R2_ROUTE_COVERAGE_SIDEBAR_L3_BEHAVIOR_AUDIT_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10.md", "ONE_SERVER_PRECHECK_R10_DEPLOYMENT_READINESS_GATE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11.md", "ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12.md", "ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13F.md", "ONE_SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14F.md", "ONE_SERVER_PRECHECK_R14F_DEPLOYMENT_EXECUTION_APPROVAL_FINAL_VERIFICATION_PASS"),
]

FALSE_FLAGS = [
    "baseRuntimeInstallationPerformedByThisPacket",
    "sshExecutedByThisPacket",
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
    ok("SERVER-DEPLOY-R1 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("SERVER-DEPLOY-R1 PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-DEPLOY-R1":
        fail("registry taskId is not SERVER-DEPLOY-R1")
    if evid.get("stage") != "SERVER-DEPLOY-R1":
        fail("evidence stage is not SERVER-DEPLOY-R1")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    if evid.get("precheckFinalApprovalReference") != "SERVER-PRECHECK-R14F":
        fail("precheckFinalApprovalReference must be SERVER-PRECHECK-R14F")
    if evid.get("deploymentExecutionFinalApprovalDecision") != "GO":
        fail("deploymentExecutionFinalApprovalDecision must be GO")
    ok("R14F GO dependency is recorded")

    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("installation, SSH, server connection, build, DB, healthcheck, smoke, and mutation flags are false")

    targets = evid.get("targetServers", {})
    for name in ["appServer", "dbServer"]:
        target = targets.get(name, {})
        for field in [
            "serverReference",
            "environmentName",
            "networkZoneReference",
            "osFamily",
            "osVersionReference",
            "installationUserReference",
            "installationWindowReference",
        ]:
            value = target.get(field, "")
            if not isinstance(value, str) or not value.startswith("RESTRICTED_"):
                fail(f"targetServers.{name}.{field} must be a restricted reference")
        expect_true(target, "cpuMemoryDiskReviewed")
        expect_pass(target, f"targetServers.{name}")
    ok("APP and DB target server inventory requirements are reviewed with restricted references")

    app = evid.get("appRuntimePlan", {})
    for field in ["pythonRuntimeRequired", "nodeRuntimeRequired", "pm2Required", "nginxRequired", "packageManagerReviewed", "runtimeVersionPlanReviewed", "installationSourceReviewed", "offlineBundleRequired"]:
        expect_true(app, field)
    expect_false(app, "installationExecutionAllowedByThisPacket")
    expect_pass(app, "appRuntimePlan")
    ok("APP runtime plan is PASS and execution is not allowed by this packet")

    db = evid.get("dbRuntimePlan", {})
    for field in ["postgresqlRequired", "postgresqlDirectionConfirmed", "databaseUserPlanReviewed", "databasePrivilegePlanReviewed", "backupToolingPlanReviewed", "restoreToolingPlanReviewed", "installationSourceReviewed", "offlineBundleRequired"]:
        expect_true(db, field)
    expect_false(db, "installationExecutionAllowedByThisPacket")
    expect_pass(db, "dbRuntimePlan")
    ok("DB runtime plan is PASS and PostgreSQL direction is confirmed")

    offline = evid.get("offlineNoDockerPlan", {})
    expect_true(offline, "offlineModePossible")
    expect_false(offline, "dockerRequired")
    for field in ["noDockerPathReviewed", "offlinePackageInventoryRequired", "offlineBundleIntegrityCheckRequired"]:
        expect_true(offline, field)
    expect_pass(offline, "offlineNoDockerPlan")
    ok("offline/no-Docker path is PASS")

    backup = evid.get("backupRollbackStopConditions", {})
    for field in ["preInstallationBackupRequired", "rollbackPlanRequired", "stopConditionsRequired", "stopConditionsReviewed", "postInstallationVerificationPlanned"]:
        expect_true(backup, field)
    expect_false(backup, "backupExecutionAllowedByThisPacket")
    expect_false(backup, "rollbackExecutionAllowedByThisPacket")
    expect_pass(backup, "backupRollbackStopConditions")
    ok("backup, rollback, and stop conditions are PASS without execution")

    secret = evid.get("secretHandling", {})
    for field in ["productionSecretStoredInPublicPacket", "productionEnvStoredInPublicPacket", "databaseUrlStoredInPublicPacket", "serverCredentialStoredInPublicPacket"]:
        expect_false(secret, field)
    expect_true(secret, "restrictedSecretReferenceOnly")
    expect_pass(secret, "secretHandling")
    ok("secret handling is PASS")

    operator = evid.get("operatorApproval", {})
    for field in ["installationOperatorAssigned", "dbOperatorAssigned", "appOperatorAssigned", "rollbackOwnerAssigned", "approvalWindowDefined", "humanApproverAssigned"]:
        expect_true(operator, field)
    expect_pass(operator, "operatorApproval")

    decision = evid.get("runtimeInstallationPlanDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeInstallationPlanDecision must be HOLD / GO / NO-GO")
    if decision != "GO":
        fail("runtimeInstallationPlanDecision must be GO for R1 completion")
    if final.get("r14fDependencyStatus") != "GO":
        fail("final r14fDependencyStatus must be GO")
    if final.get("runtimeInstallationPlanDecision") != "GO":
        fail("final runtimeInstallationPlanDecision must be GO")
    ok("runtimeInstallationPlanDecision is GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("MENU-GA-R1/R2 and SERVER-PRECHECK R10/R11/R12/R13F/R14F source markers exist")

    check_no_executable_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-DEPLOY-R1 Base Runtime Installation Plan validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
