#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R8.md"
PACKET_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R8_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r8/server-precheck-r8.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r8/server-precheck-r8.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r8/server-precheck-r8.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r8/server-precheck-r8.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R1.md",
        "ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R2.md",
        "ONE_SERVER_PRECHECK_R2_READONLY_ACCESS_WINDOW_PLAN_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R3.md",
        "ONE_SERVER_PRECHECK_R3_ACTUAL_READONLY_OBSERVATION_PLAN_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md",
        "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R4F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5.md",
        "ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R5F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6.md",
        "ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R6F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R7.md",
        "ONE_SERVER_PRECHECK_R7_HUMAN_APPROVAL_RECORD_AND_OBSERVATION_WINDOW_LOCK_PASS",
    ),
    (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R7_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R7F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
]

REQUIRED_PACKET_FIELDS = [
    "packetId",
    "stage",
    "approvalReference",
    "observationWindowReference",
    "observationStatus",
    "observer",
    "approver",
    "targetServers",
    "approvedServices",
    "approvedPaths",
    "observationStartTime",
    "observationEndTime",
    "commandsReviewedOnly",
    "sshExecutedByThisPacket",
    "serverMutationPerformed",
    "dbMutationPerformed",
    "authMutationPerformed",
    "runtimeMutationPerformed",
    "rawEvidenceAllowed",
    "redactedEvidenceRequired",
    "evidenceItems",
    "redactionChecklist",
    "archiveLocation",
    "reviewStatus",
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
    "actualObservationExecutionAllowed",
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
                fail(
                    f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}"
                )
    ok("no executable server operation steps found in executable block scope")


def main():
    required_files = [DOC, PACKET_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R8 documents, registry, evidence, validation, final verification, release index, and validator exist")

    marker_files = [DOC, PACKET_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]
    for path in marker_files:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R8 PASS marker exists in document, command packet, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R8":
        fail("registry taskId is not SERVER-PRECHECK-R8")
    if reg.get("mode") != "manual-observation-evidence-packet-only":
        fail("registry mode is not manual-observation-evidence-packet-only")
    if reg.get("passMarker") != PASS:
        fail("registry pass marker mismatch")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification metadata are correct")

    if evid.get("stage") != "SERVER-PRECHECK-R8":
        fail("evidence stage must be SERVER-PRECHECK-R8")
    if evid.get("approvalReference") != "SERVER-PRECHECK-R7":
        fail("approvalReference must be SERVER-PRECHECK-R7")
    if evid.get("observationWindowReference") != "SERVER-PRECHECK-R7":
        fail("observationWindowReference must be SERVER-PRECHECK-R7")
    if evid.get("observationStatus") != "NOT_EXECUTED":
        fail("observationStatus must be NOT_EXECUTED")
    ok("evidence stage and R7 references are correct")

    for field in REQUIRED_PACKET_FIELDS:
        if field not in evid:
            fail(f"required evidence packet field missing: {field}")
        if field not in reg.get("requiredPacketFields", []):
            fail(f"required packet field missing from registry: {field}")
    ok("required evidence packet fields are present")

    if evid.get("commandsReviewedOnly") is not True:
        fail("commandsReviewedOnly must be true")
    for key in [
        "sshExecutedByThisPacket",
        "serverMutationPerformed",
        "dbMutationPerformed",
        "authMutationPerformed",
        "runtimeMutationPerformed",
        "rawEvidenceAllowed",
    ]:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    if evid.get("redactedEvidenceRequired") is not True:
        fail("redactedEvidenceRequired must be true")
    ok("evidence read-only and redaction flags are correct")

    if not isinstance(evid.get("evidenceItems"), list):
        fail("evidenceItems must exist as a list")
    if evid.get("redactionChecklist") != REDACTION_CHECKLIST:
        fail("redactionChecklist must match the required R8 checklist")
    if reg.get("redactionChecklistRequired") != REDACTION_CHECKLIST:
        fail("registry redactionChecklistRequired must match the required R8 checklist")
    ok("evidence item list and redaction checklist exist")

    if evid.get("reviewStatus") not in ["HOLD", "ACCEPTED", "REJECTED"]:
        fail("reviewStatus must be HOLD / ACCEPTED / REJECTED")
    if evid.get("closureDecision") not in ["HOLD", "GO", "NO-GO"]:
        fail("closureDecision must be HOLD / GO / NO-GO")
    for state in ["HOLD", "ACCEPTED", "REJECTED"]:
        if state not in reg.get("allowedPacketReviewStatuses", []):
            fail(f"registry missing packet review status: {state}")
    for state in ["HOLD", "GO", "NO-GO"]:
        if state not in reg.get("allowedClosureDecisions", []):
            fail(f"registry missing closure decision: {state}")
    ok("review status and closure decision models are correct")

    item_model = evid.get("evidenceItemModel", {})
    for field in [
        "evidenceId",
        "sourceType",
        "sourceDescription",
        "collectionMethod",
        "containsSecret",
        "containsCredential",
        "containsToken",
        "containsPrivateIp",
        "containsHostname",
        "containsUsername",
        "redactionStatus",
        "redactedArtifactReference",
        "reviewStatus",
        "reviewerNotes",
    ]:
        if field not in item_model:
            fail(f"evidence item model missing field: {field}")
    if item_model.get("sourceType") not in reg.get("allowedEvidenceSourceTypes", []):
        fail("evidence item sourceType model is invalid")
    if item_model.get("redactionStatus") not in reg.get("allowedEvidenceRedactionStatuses", []):
        fail("evidence item redactionStatus model is invalid")
    if item_model.get("reviewStatus") not in reg.get("allowedEvidenceReviewStatuses", []):
        fail("evidence item reviewStatus model is invalid")
    ok("evidence item model is complete")

    boundaries = reg.get("boundaries", {})
    final_boundaries = final.get("boundaries", {})
    for key in FALSE_BOUNDARIES:
        if boundaries.get(key) is not False:
            fail(f"registry boundary must be false: {key}")
        if final_boundaries.get(key) is not False:
            fail(f"final verification boundary must be false: {key}")
    if reg.get("publicReleaseRules", {}).get("redactedEvidenceRequired") is not True:
        fail("public release redacted evidence requirement must be true")
    if reg.get("publicReleaseRules", {}).get("rawEvidenceAllowed") is not False:
        fail("raw evidence must not be allowed in public release")
    ok("registry and final verification boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R7F source markers exist")

    check_no_executable_server_steps([DOC, PACKET_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R8 Manual Observation Evidence Packet validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
