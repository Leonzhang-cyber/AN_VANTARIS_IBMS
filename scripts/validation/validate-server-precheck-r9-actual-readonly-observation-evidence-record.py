#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R9.md"
RECORD_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R9_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r9/server-precheck-r9.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r9/server-precheck-r9.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r9/server-precheck-r9.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r9/server-precheck-r9.final-verification.json"
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
]

REQUIRED_RECORD_FIELDS = [
    "recordId",
    "stage",
    "approvalReference",
    "evidencePacketReference",
    "observationPlanReference",
    "manualCommandPackReference",
    "observationPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "serverMutationPerformed",
    "dbMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "deploymentPerformed",
    "installPerformed",
    "observationStatus",
    "observationWindowStatus",
    "observer",
    "reviewer",
    "approver",
    "targetEnvironment",
    "observationSession",
    "appServerEvidence",
    "dbServerEvidence",
    "crossServerEvidence",
    "redactionChecklist",
    "restrictedEvidenceReferences",
    "publicEvidenceReferences",
    "findingSummary",
    "closureDecision",
    "notes",
]

REDACTION_CHECKLIST = [
    "Password",
    "Token",
    "API key",
    "JWT",
    "Private key",
    "Secret",
    "SSH key",
    "Database URL",
    "Internal hostname",
    "Private IP",
    "Username",
    "Email",
    "Customer-specific server name",
    "Production path with sensitive naming",
]

FALSE_RECORD_FLAGS = [
    "observationPerformedByThisPacket",
    "sshExecutedByThisPacket",
    "serverMutationPerformed",
    "dbMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "frontendBackendMutationPerformed",
    "deploymentPerformed",
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
    "authMutationAllowed",
    "runtimeMutationAllowed",
    "frontendChanged",
    "backendChanged",
    "routesChanged",
    "productionConfigMutationAllowed",
    "actualObservationExecutionByThisPacketAllowed",
]

APP_ITEM_FIELDS = [
    "evidenceId",
    "serverRole",
    "evidenceType",
    "sourceDescription",
    "collectionMode",
    "actualCommandTextStored",
    "rawOutputStored",
    "redactedOutputStored",
    "redactedArtifactReference",
    "containsSecret",
    "containsCredential",
    "containsToken",
    "containsPrivateIp",
    "containsHostname",
    "containsUsername",
    "observationResult",
    "findingSeverity",
    "reviewStatus",
    "reviewerNotes",
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


def check_item_model(model, role, allowed_types, reg, label):
    for field in APP_ITEM_FIELDS:
        if field not in model:
            fail(f"{label} evidence item model missing field: {field}")
    if model.get("serverRole") != role:
        fail(f"{label} evidence item serverRole must be {role}")
    if model.get("evidenceType") not in allowed_types:
        fail(f"{label} evidenceType is not allowed")
    if model.get("collectionMode") != "manual-readonly":
        fail(f"{label} collectionMode must be manual-readonly")
    for key in [
        "actualCommandTextStored",
        "rawOutputStored",
        "containsSecret",
        "containsCredential",
        "containsToken",
        "containsPrivateIp",
        "containsHostname",
        "containsUsername",
    ]:
        if model.get(key) is not False:
            fail(f"{label} {key} must be false")
    if model.get("redactedOutputStored") is not True:
        fail(f"{label} redactedOutputStored must be true")
    if model.get("observationResult") not in reg.get("allowedObservationResults", []):
        fail(f"{label} observationResult is invalid")
    if model.get("findingSeverity") not in reg.get("allowedFindingSeverities", []):
        fail(f"{label} findingSeverity is invalid")
    if model.get("reviewStatus") not in reg.get("allowedReviewStatuses", []):
        fail(f"{label} reviewStatus is invalid")


def main():
    required_files = [DOC, RECORD_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R9 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, RECORD_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R9 PASS marker exists in document, record, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R9":
        fail("registry taskId is not SERVER-PRECHECK-R9")
    if reg.get("mode") != "actual-readonly-observation-evidence-record-only":
        fail("registry mode is not actual-readonly-observation-evidence-record-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R9",
        "approvalReference": "SERVER-PRECHECK-R7",
        "evidencePacketReference": "SERVER-PRECHECK-R8",
        "observationPlanReference": "SERVER-PRECHECK-R3",
        "manualCommandPackReference": "SERVER-PRECHECK-R6",
        "observationWindowStatus": "LOCKED_BY_R7",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and R7/R8/R3/R6 references are correct")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in evid:
            fail(f"required evidence record field missing: {field}")
        if field not in reg.get("requiredRecordFields", []):
            fail(f"required record field missing from registry: {field}")
    ok("required evidence record fields are present")

    for key in FALSE_RECORD_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    if evid.get("observationStatus") not in reg.get("allowedObservationStatuses", []):
        fail("observationStatus is invalid")
    session = evid.get("observationSession", {})
    if session.get("manualReadonlyOnly") is not True:
        fail("manualReadonlyOnly must be true")
    ok("evidence execution and mutation flags are false")

    for key in ["appServerEvidence", "dbServerEvidence", "crossServerEvidence", "restrictedEvidenceReferences", "publicEvidenceReferences"]:
        if not isinstance(evid.get(key), list):
            fail(f"{key} must exist as a list")
    if evid.get("redactionChecklist") != REDACTION_CHECKLIST:
        fail("redactionChecklist must match the required R9 checklist")
    if reg.get("redactionChecklistRequired") != REDACTION_CHECKLIST:
        fail("registry redactionChecklistRequired must match the required R9 checklist")
    ok("APP/DB/cross evidence lists and redaction/reference lists exist")

    if evid.get("closureDecision") not in ["HOLD", "GO", "NO-GO"]:
        fail("closureDecision must be HOLD / GO / NO-GO")
    if evid.get("reviewer", {}).get("reviewStatus") not in reg.get("allowedReviewStatuses", []):
        fail("reviewer reviewStatus is invalid")
    if evid.get("approver", {}).get("approvalStatus") not in reg.get("allowedApprovalStatuses", []):
        fail("approver approvalStatus is invalid")
    for state in ["HOLD", "GO", "NO-GO"]:
        if state not in reg.get("allowedClosureDecisions", []):
            fail(f"registry missing closure decision: {state}")
    ok("review, approval, and closure decision models are correct")

    finding_summary = evid.get("findingSummary", {})
    for key in ["criticalFindings", "majorFindings", "minorFindings", "informationalFindings"]:
        if not isinstance(finding_summary.get(key), int):
            fail(f"findingSummary {key} must be an integer")
    ok("finding summary model is correct")

    check_item_model(
        evid.get("appServerEvidenceItemModel", {}),
        "APP",
        reg.get("allowedAppEvidenceTypes", []),
        reg,
        "APP",
    )
    check_item_model(
        evid.get("dbServerEvidenceItemModel", {}),
        "DB",
        reg.get("allowedDbEvidenceTypes", []),
        reg,
        "DB",
    )
    ok("APP and DB evidence item models are complete")

    boundaries = reg.get("boundaries", {})
    final_boundaries = final.get("boundaries", {})
    for key in FALSE_BOUNDARIES:
        if boundaries.get(key) is not False:
            fail(f"registry boundary must be false: {key}")
        if final_boundaries.get(key) is not False:
            fail(f"final verification boundary must be false: {key}")
    rules = reg.get("publicReleaseRules", {})
    if rules.get("rawEvidenceAllowedInPublicPacket") is not False:
        fail("raw evidence must not be allowed in public release packet")
    if rules.get("actualCommandTextStoredByDefault") is not False:
        fail("actual command text must not be stored by default")
    if rules.get("redactedOutputReferencesOnly") is not True:
        fail("public release must use redacted output references only")
    ok("registry and final verification boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R8 source markers exist")

    check_no_executable_server_steps([DOC, RECORD_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R9 Actual Read-only Observation Evidence Record validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
