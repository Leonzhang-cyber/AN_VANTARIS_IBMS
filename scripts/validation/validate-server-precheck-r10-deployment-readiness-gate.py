#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R10_DEPLOYMENT_READINESS_GATE_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10.md"
GATE_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10_DEPLOYMENT_READINESS_GATE.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R10_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r10/server-precheck-r10.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r10/server-precheck-r10.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r10/server-precheck-r10.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r10/server-precheck-r10.final-verification.json"
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
]

REQUIRED_GATE_FIELDS = [
    "gateId",
    "stage",
    "approvalReference",
    "manualEvidencePacketReference",
    "actualObservationEvidenceReference",
    "deploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "serverMutationPerformed",
    "dbMutationPerformed",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "installPerformed",
    "evidenceChainStatus",
    "appServerReadiness",
    "dbServerReadiness",
    "backupRollbackReadiness",
    "secretHandlingReadiness",
    "consoleGaVerificationDependency",
    "reviewer",
    "approver",
    "gateDecision",
    "notes",
]

FALSE_GATE_FLAGS = [
    "deploymentPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "serverMutationPerformed",
    "dbMutationPerformed",
    "dbMigrationPerformed",
    "dbBackupPerformed",
    "dbRestorePerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "installPerformed",
]

FALSE_BOUNDARIES = [
    "sshExecutionAllowed",
    "sshAutomationAllowed",
    "sshConnectionCommandIncluded",
    "executableScriptAllowed",
    "deploymentAllowed",
    "installAllowed",
    "appServerMutationAllowed",
    "dbServerMutationAllowed",
    "dbMigrationAllowed",
    "dbBackupExecutionAllowed",
    "dbRestoreExecutionAllowed",
    "authMutationAllowed",
    "runtimeMutationAllowed",
    "frontendChanged",
    "backendChanged",
    "routesChanged",
    "productionConfigMutationAllowed",
    "actualDeploymentExecutionByThisPacketAllowed",
]

EXECUTABLE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal"}
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
    r"(^|\s)pg_dump\b",
    r"(^|\s)pg_restore\b",
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


def check_no_executable_server_steps(paths):
    executable_scope = []
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang in EXECUTABLE_LANGS:
                executable_scope.append((path, body))

    for path, body in executable_scope:
        for pattern in FORBIDDEN_EXEC_PATTERNS:
            if re.search(pattern, body, flags=re.IGNORECASE):
                fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server operation steps found in executable block scope")


def check_readiness_status(section, allowed, label):
    if not isinstance(section, dict):
        fail(f"{label} must be an object")
    if section.get("readinessStatus") not in allowed:
        fail(f"{label} readinessStatus is invalid")


def main():
    required_files = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R10 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R10 PASS marker exists in document, gate, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R10":
        fail("registry taskId is not SERVER-PRECHECK-R10")
    if reg.get("mode") != "deployment-readiness-gate-only":
        fail("registry mode is not deployment-readiness-gate-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R10",
        "approvalReference": "SERVER-PRECHECK-R7",
        "manualEvidencePacketReference": "SERVER-PRECHECK-R8",
        "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and R7/R8/R9 references are correct")

    for field in REQUIRED_GATE_FIELDS:
        if field not in evid:
            fail(f"required gate field missing: {field}")
        if field not in reg.get("requiredGateFields", []):
            fail(f"required gate field missing from registry: {field}")
    ok("required deployment readiness gate fields are present")

    for key in FALSE_GATE_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    ok("deployment, SSH, install, backup, restore, migration, and mutation flags are false")

    allowed_gate = reg.get("allowedGateDecisions", [])
    allowed_readiness = reg.get("allowedReadinessStatuses", [])
    if evid.get("evidenceChainStatus") not in reg.get("allowedEvidenceChainStatuses", []):
        fail("evidenceChainStatus is invalid")
    if evid.get("gateDecision") not in allowed_gate:
        fail("gateDecision must be HOLD / GO / NO-GO")
    check_readiness_status(evid.get("appServerReadiness"), allowed_readiness, "appServerReadiness")
    check_readiness_status(evid.get("dbServerReadiness"), allowed_readiness, "dbServerReadiness")
    check_readiness_status(evid.get("backupRollbackReadiness"), allowed_readiness, "backupRollbackReadiness")
    check_readiness_status(evid.get("secretHandlingReadiness"), allowed_readiness, "secretHandlingReadiness")
    check_readiness_status(evid.get("consoleGaVerificationDependency"), allowed_readiness, "consoleGaVerificationDependency")
    ok("evidence chain, readiness, and gate decision models are correct")

    backup = evid.get("backupRollbackReadiness", {})
    if backup.get("backupRequiredBeforeDeployment") is not True:
        fail("backupRequiredBeforeDeployment must be true")
    if backup.get("backupExecutionAllowedByThisPacket") is not False:
        fail("backupExecutionAllowedByThisPacket must be false")
    if backup.get("rollbackPlanRequired") is not True:
        fail("rollbackPlanRequired must be true")
    if backup.get("rollbackExecutionAllowedByThisPacket") is not False:
        fail("rollbackExecutionAllowedByThisPacket must be false")
    ok("backup and rollback readiness requirements are correct")

    secret = evid.get("secretHandlingReadiness", {})
    if secret.get("secretsStoredInPublicPacket") is not False:
        fail("secretsStoredInPublicPacket must be false")
    if secret.get("productionEnvStoredInPublicPacket") is not False:
        fail("productionEnvStoredInPublicPacket must be false")
    if secret.get("restrictedSecretReferenceOnly") is not True:
        fail("restrictedSecretReferenceOnly must be true")
    ok("secret and production env handling requirements are correct")

    console = evid.get("consoleGaVerificationDependency", {})
    if console.get("required") is not True:
        fail("consoleGaVerificationDependency.required must be true")
    if console.get("plannedStage") != "SERVER-PRECHECK-R13":
        fail("consoleGaVerificationDependency.plannedStage must be SERVER-PRECHECK-R13")
    if console.get("menuArchitectureBaselineReference") != "MENU-GA-R1/R2":
        fail("menuArchitectureBaselineReference must be MENU-GA-R1/R2")
    ok("Console International GA verification dependency is correct")

    reviewer_status = evid.get("reviewer", {}).get("reviewStatus")
    approver_status = evid.get("approver", {}).get("approvalStatus")
    if reviewer_status not in reg.get("allowedReviewStatuses", []):
        fail("reviewer reviewStatus is invalid")
    if approver_status not in reg.get("allowedApprovalStatuses", []):
        fail("approver approvalStatus is invalid")
    ok("reviewer and approver models are correct")

    boundaries = reg.get("boundaries", {})
    final_boundaries = final.get("boundaries", {})
    for key in FALSE_BOUNDARIES:
        if boundaries.get(key) is not False:
            fail(f"registry boundary must be false: {key}")
        if final_boundaries.get(key) is not False:
            fail(f"final verification boundary must be false: {key}")
    rules = reg.get("secretHandlingRules", {})
    if rules.get("productionCredentialsInPublicReleaseIndexAllowed") is not False:
        fail("production credentials must not be allowed in public release index")
    if rules.get("productionEnvContentCommittedAllowed") is not False:
        fail("production .env content must not be committed")
    if rules.get("restrictedSecretReferenceOnly") is not True:
        fail("registry restrictedSecretReferenceOnly must be true")
    ok("registry and final verification boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R9 source markers exist")

    check_no_executable_server_steps([DOC, GATE_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R10 Deployment Readiness Gate validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
