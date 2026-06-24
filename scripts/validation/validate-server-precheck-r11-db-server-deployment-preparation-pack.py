#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r11/server-precheck-r11.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r11/server-precheck-r11.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r11/server-precheck-r11.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r11/server-precheck-r11.final-verification.json"
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
]

REQUIRED_PACK_FIELDS = [
    "packId",
    "stage",
    "deploymentReadinessGateReference",
    "approvalReference",
    "actualObservationEvidenceReference",
    "dbDeploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "dbServerConnectionPerformed",
    "postgresCommandExecuted",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "dbSeedPerformed",
    "dbUserCreated",
    "dbPrivilegeMutationPerformed",
    "serverMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "productionConfigMutationPerformed",
    "postgresqlDirectionConfirmed",
    "targetDbServer",
    "migrationPreparation",
    "backupPreparation",
    "rollbackPreparation",
    "seedPreparation",
    "appDbConnectionPreparation",
    "secretHandling",
    "reviewer",
    "approver",
    "preparationDecision",
    "notes",
]

FALSE_PACK_FLAGS = [
    "dbDeploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "dbServerConnectionPerformed",
    "postgresCommandExecuted",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "dbSeedPerformed",
    "dbUserCreated",
    "dbPrivilegeMutationPerformed",
    "serverMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "productionConfigMutationPerformed",
]

FALSE_BOUNDARIES = [
    "sshExecutionAllowed",
    "sshAutomationAllowed",
    "sshConnectionCommandIncluded",
    "executableScriptAllowed",
    "dbServerConnectionAllowed",
    "postgresCommandExecutionAllowed",
    "deploymentAllowed",
    "installAllowed",
    "dbMigrationAllowed",
    "dbBackupExecutionAllowed",
    "dbRestoreExecutionAllowed",
    "dbSeedExecutionAllowed",
    "dbUserCreationAllowed",
    "dbPrivilegeMutationAllowed",
    "appServerMutationAllowed",
    "dbServerMutationAllowed",
    "authMutationAllowed",
    "runtimeMutationAllowed",
    "frontendChanged",
    "backendChanged",
    "routesChanged",
    "productionConfigMutationAllowed",
    "productionCredentialPublicStorageAllowed",
    "actualDbDeploymentExecutionByThisPacketAllowed",
]

EXECUTABLE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal", "sql"}
FORBIDDEN_EXEC_PATTERNS = [
    r"(^|\s)ssh\s+\S+@",
    r"(^|\s)ssh\s+-i\b",
    r"(^|\s)scp\b",
    r"(^|\s)rsync\b",
    r"(^|\s)sudo\b",
    r"\bsystemctl\s+restart\b",
    r"\bdocker\s+compose\s+up\b",
    r"\bnpm\s+run\s+dev\b",
    r"\bpm2\s+restart\b",
    r"\bprisma\s+migrate\b",
    r"\bflask\s+run\b",
    r"\bgunicorn\b",
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
    r"\bcurl\b.*\b(production|prod)\b.*\b(mutate|mutation|write|delete|post|put|patch)\b",
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


def check_no_executable_db_steps(paths):
    executable_scope = []
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang in EXECUTABLE_LANGS:
                executable_scope.append((path, body))
    for path, body in executable_scope:
        for pattern in FORBIDDEN_EXEC_PATTERNS:
            if re.search(pattern, body, flags=re.IGNORECASE):
                fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server or DB operation steps found in executable block scope")


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
    ok("R11 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R11 PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R11":
        fail("registry taskId is not SERVER-PRECHECK-R11")
    if reg.get("mode") != "db-server-deployment-preparation-pack-only":
        fail("registry mode is not db-server-deployment-preparation-pack-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R11",
        "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
        "approvalReference": "SERVER-PRECHECK-R7",
        "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and R10/R7/R9 references are correct")

    for field in REQUIRED_PACK_FIELDS:
        if field not in evid:
            fail(f"required pack field missing: {field}")
        if field not in reg.get("requiredPackFields", []):
            fail(f"required pack field missing from registry: {field}")
    ok("required DB preparation pack fields are present")

    for key in FALSE_PACK_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    ok("DB deployment, SSH, connection, command, migration, backup, restore, seed, user, privilege, and mutation flags are false")

    if evid.get("postgresqlDirectionConfirmed") is not True:
        fail("postgresqlDirectionConfirmed must be true")
    if evid.get("targetDbServer", {}).get("dbEngine") != "PostgreSQL":
        fail("targetDbServer.dbEngine must be PostgreSQL")
    if reg.get("targetDbEngine") != "PostgreSQL":
        fail("registry targetDbEngine must be PostgreSQL")
    if reg.get("mysqlTargetArchitectureAllowed") is not False:
        fail("MySQL target architecture must not be allowed")
    ok("PostgreSQL direction is confirmed and MySQL target architecture is not reintroduced")

    allowed_readiness = reg.get("allowedReadinessStatuses", [])
    for key in [
        "migrationPreparation",
        "backupPreparation",
        "rollbackPreparation",
        "seedPreparation",
        "appDbConnectionPreparation",
        "secretHandling",
    ]:
        check_readiness(evid.get(key), allowed_readiness, key)

    migration = evid.get("migrationPreparation", {})
    if migration.get("migrationDryRunRequired") is not True:
        fail("migrationDryRunRequired must be true")
    if migration.get("migrationExecutionAllowedByThisPacket") is not False:
        fail("migrationExecutionAllowedByThisPacket must be false")

    backup = evid.get("backupPreparation", {})
    if backup.get("backupRequiredBeforeMigration") is not True:
        fail("backupRequiredBeforeMigration must be true")
    if backup.get("backupExecutionAllowedByThisPacket") is not False:
        fail("backupExecutionAllowedByThisPacket must be false")

    rollback = evid.get("rollbackPreparation", {})
    if rollback.get("rollbackPlanRequired") is not True:
        fail("rollbackPlanRequired must be true")
    if rollback.get("restoreExecutionAllowedByThisPacket") is not False:
        fail("restoreExecutionAllowedByThisPacket must be false")

    seed = evid.get("seedPreparation", {})
    if seed.get("seedExecutionAllowedByThisPacket") is not False:
        fail("seedExecutionAllowedByThisPacket must be false")
    ok("migration, backup, rollback, and seed preparation requirements are correct")

    app_db = evid.get("appDbConnectionPreparation", {})
    if app_db.get("databaseUrlStoredInPublicPacket") is not False:
        fail("appDbConnectionPreparation.databaseUrlStoredInPublicPacket must be false")
    if app_db.get("restrictedCredentialReferenceOnly") is not True:
        fail("restrictedCredentialReferenceOnly must be true")

    secret = evid.get("secretHandling", {})
    if secret.get("productionDbPasswordStoredInPublicPacket") is not False:
        fail("productionDbPasswordStoredInPublicPacket must be false")
    if secret.get("databaseUrlStoredInPublicPacket") is not False:
        fail("secretHandling.databaseUrlStoredInPublicPacket must be false")
    if secret.get("restrictedSecretReferenceOnly") is not True:
        fail("restrictedSecretReferenceOnly must be true")
    ok("APP-to-DB connection and secret handling requirements are correct")

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
    if rules.get("productionDbPasswordStoredInPublicPacket") is not False:
        fail("registry productionDbPasswordStoredInPublicPacket must be false")
    if rules.get("databaseUrlStoredInPublicPacket") is not False:
        fail("registry databaseUrlStoredInPublicPacket must be false")
    if rules.get("restrictedSecretReferenceOnly") is not True:
        fail("registry restrictedSecretReferenceOnly must be true")
    ok("registry and final verification boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R10 source markers exist")

    check_no_executable_db_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R11 DB Server Deployment Preparation Pack validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
