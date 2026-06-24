#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R7_HUMAN_APPROVAL_RECORD_AND_OBSERVATION_WINDOW_LOCK_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R7.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r7/server-precheck-r7.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r7/server-precheck-r7.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r7/server-precheck-r7.validation.json"

SOURCE_DOCS = [
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md",
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4_FINAL_VERIFICATION_NOTE.md",
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5.md",
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5_FINAL_VERIFICATION_NOTE.md",
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6.md",
    ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6_FINAL_VERIFICATION_NOTE.md"
]

SOURCE_MARKERS = [
    "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS",
    "ONE_SERVER_PRECHECK_R4F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    "ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS",
    "ONE_SERVER_PRECHECK_R5F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    "ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS",
    "ONE_SERVER_PRECHECK_R6F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS"
]

FORBIDDEN_CODE_PATTERNS = [
    r"\bssh\b",
    r"\bscp\b",
    r"\brsync\b",
    r"\bsudo\b",
    r"systemctl\s+restart",
    r"systemctl\s+stop",
    r"systemctl\s+start",
    r"npm\s+install",
    r"pip\s+install",
    r"password\s*[:=]",
    r"token\s*[:=]",
    r"secret\s*[:=]",
    r"private[_ -]?key\s*[:=]",
    r"credential\s*[:=]"
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

def strip_docs(text):
    # R7 contains boundary prose mentioning SSH/secrets as denied behavior.
    # The forbidden scan is meant to detect assignment or command-like content.
    text = re.sub(r"## Boundary Statement.*?## Next Task If Approved", "## Next Task If Approved", text, flags=re.S)
    text = re.sub(r"## Stop Conditions.*?## Boundary Statement", "## Boundary Statement", text, flags=re.S)
    return text

def main():
    required = [DOC, REG, EVID, VAL, Path(__file__)]
    for path in required:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("required R7 document, registry, evidence, validation, and validator files exist")

    texts = [read(DOC), read(REG), read(EVID), read(VAL)]
    if not all(PASS in text for text in texts):
        fail("R7 PASS marker missing from document or JSON registries")
    ok("R7 PASS marker exists in document and JSON registries")

    reg = load_json(REG)
    if reg.get("taskId") != "SERVER-PRECHECK-R7":
        fail("registry taskId is not SERVER-PRECHECK-R7")
    if reg.get("mode") != "approval-record-and-window-lock-only":
        fail("registry mode must be approval-record-and-window-lock-only")
    if reg.get("defaultApprovalStatus") != "HOLD":
        fail("defaultApprovalStatus must be HOLD")
    for state in ["HOLD", "GO", "NO-GO"]:
        if state not in reg.get("approvalStatusAllowed", []):
            fail(f"missing approval status: {state}")
    ok("approval status model is correct")

    required_fields = [
        "approvalStatus",
        "approverName",
        "approverRole",
        "operatorName",
        "operatorRole",
        "observationWindowStart",
        "observationWindowEnd",
        "timezone",
        "targetServerIdentity",
        "targetServerRole",
        "approvedServices",
        "approvedPaths",
        "approvedNonSecretFiles",
        "approvedEvidenceLocation",
        "redactionPolicy",
        "stopConditions",
        "noGoConditions",
        "approvalRecordedAt"
    ]
    for field in required_fields:
        if field not in reg.get("requiredApprovalFields", []):
            fail(f"missing approval field: {field}")
    ok("required approval and window lock fields exist")

    boundaries = reg.get("boundaries", {})
    for key in [
        "sshExecutionAllowed", "sshAutomationAllowed", "sshConnectionCommandIncluded",
        "executableScriptAllowed", "observationCommandPackChanged", "deploymentAllowed",
        "installAllowed", "dbMutationAllowed", "authMutationAllowed", "secretsMutationAllowed",
        "runtimeActionAllowed", "frontendChanged", "backendChanged", "routesChanged",
        "menuGaR1Changed", "menuGaR2Changed"
    ]:
        if boundaries.get(key) is not False:
            fail(f"boundary {key} must be false")
    if reg.get("windowLockRequiredBeforeObservation") is not True:
        fail("windowLockRequiredBeforeObservation must be true")
    if reg.get("humanApprovalRequiredBeforeObservation") is not True:
        fail("humanApprovalRequiredBeforeObservation must be true")
    ok("registry boundaries, human approval, and window lock requirements are correct")

    for source, marker in zip(SOURCE_DOCS, SOURCE_MARKERS):
        if marker not in read(source):
            fail(f"missing source marker {marker} in {source.relative_to(ROOT)}")
    ok("R4/R4F/R5/R5F/R6/R6F source markers exist")

    # R7 is an approval/window-lock document and intentionally contains denial
    # language such as "sshExecutionAllowed: false" and "does not execute SSH".
    # Only executable-looking fenced command blocks should be scanned for command tokens.
    fenced_blocks = []
    for text in texts:
        in_block = False
        current = []
        for line in text.splitlines():
            if line.startswith("```"):
                if in_block:
                    fenced_blocks.append("\n".join(current))
                    current = []
                    in_block = False
                else:
                    in_block = True
                continue
            if in_block:
                current.append(line)

    scan = "\n".join(fenced_blocks)
    for pattern in FORBIDDEN_CODE_PATTERNS:
        if re.search(pattern, scan, flags=re.IGNORECASE):
            fail(f"forbidden command/secret assignment token appears in R7 executable block scope: {pattern}")
    ok("no SSH command, automation, forbidden command, or secret assignment exists in executable block scope")

    ok("R7 remains approval-record-and-window-lock-only")
    print(PASS)

if __name__ == "__main__":
    main()
