#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5.md"
REG_DIR = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r5"
REG = REG_DIR / "server-precheck-r5.registry.json"
EVID = REG_DIR / "server-precheck-r5.evidence.json"
VAL = REG_DIR / "server-precheck-r5.validation.json"

R4_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md"
R4F_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4_FINAL_VERIFICATION_NOTE.md"

R4_PASS = "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS"
R4F_PASS = "ONE_SERVER_PRECHECK_R4F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS"

FORBIDDEN_FILES = [
    "AN_VANTARIS_IBMS-frontend/src",
    "AN_VANTARIS_IBMS-backend/src",
    "AN_VANTARIS_ONE/MENU_GA_R1",
    "AN_VANTARIS_ONE/registries/menu-ga-r1",
    "AN_VANTARIS_ONE/MENU_GA_R2",
    "AN_VANTARIS_ONE/registries/menu-ga-r2",
]

FORBIDDEN_EXECUTION_TOKENS = [
    "subprocess",
    "paramiko",
    "fabric",
    "sshpass",
    "scp ",
    "rsync ",
    "systemctl restart",
    "systemctl stop",
    "systemctl start",
    "docker",
    "kubectl",
    "npm install",
    "pip install",
    "apt ",
    "yum ",
    "dnf ",
    "chmod",
    "chown",
    "rm -rf",
    "PRIVATE KEY",
]

SECRET_PATTERNS = [
    r"password\s*[:=]",
    r"token\s*[:=]",
    r"secret\s*[:=]",
    r"private[_ -]?key\s*[:=]",
]

def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)

def ok(msg: str) -> None:
    print(f"[PASS] {msg}")

def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")

def load_json(path: Path):
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")

def main() -> None:
    files = [DOC, REG, EVID, VAL, Path(__file__)]
    for f in files:
        if not f.exists():
            fail(f"required file missing: {f}")
    ok("required R5 document, registry, evidence, validation, and validator files exist")

    texts = [read(DOC), read(REG), read(EVID), read(VAL)]
    if not all(PASS in t for t in texts):
        fail("R5 PASS marker missing from document or JSON registries")
    ok("R5 PASS marker exists in document and JSON registries")

    reg = load_json(REG)
    if reg.get("taskId") != "SERVER-PRECHECK-R5":
        fail("registry taskId is not SERVER-PRECHECK-R5")
    if reg.get("mode") != "entry-gate-only":
        fail("registry mode must be entry-gate-only")
    if reg.get("defaultDecisionState") != "HOLD":
        fail("default decision state must be HOLD")
    for state in ["GO", "HOLD", "NO-GO"]:
        if state not in reg.get("decisionStates", []):
            fail(f"missing decision state: {state}")
    ok("registry task, mode, and decision states are correct")

    boundaries = reg.get("boundaries", {})
    false_required = [
        "sshExecutionAllowed",
        "sshAutomationAllowed",
        "deploymentAllowed",
        "installAllowed",
        "dbMutationAllowed",
        "authMutationAllowed",
        "secretsMutationAllowed",
        "runtimeActionAllowed",
        "frontendChanged",
        "backendChanged",
        "routesChanged",
        "menuGaR1Changed",
        "menuGaR2Changed",
    ]
    for key in false_required:
        if boundaries.get(key) is not False:
            fail(f"boundary {key} must be false")
    if reg.get("humanApprovalRequired") is not True:
        fail("humanApprovalRequired must be true")
    ok("registry boundary flags and human approval requirement are correct")

    approval_fields = reg.get("approvalFieldsRequired", [])
    for field in [
        "observationWindow",
        "operator",
        "approver",
        "targetServerIdentity",
        "approvedServices",
        "approvedPaths",
        "readOnlyCommandCategories",
        "redactionPolicy",
        "stopConditions",
        "evidenceStorageLocation",
    ]:
        if field not in approval_fields:
            fail(f"missing approval field: {field}")
    if len(reg.get("stopConditions", [])) < 8:
        fail("stop conditions list is incomplete")
    ok("approval fields and stop conditions are present")

    r4_text = read(R4_DOC)
    r4f_text = read(R4F_DOC)
    if R4_PASS not in r4_text:
        fail("R4 source PASS marker missing")
    if R4F_PASS not in r4f_text:
        fail("R4F source PASS marker missing")
    ok("R4 and R4F source PASS markers exist")

    joined = "\n".join(texts)
    for token in FORBIDDEN_EXECUTION_TOKENS:
        if token in joined:
            fail(f"forbidden execution token appears in R5 scope: {token}")

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, joined, flags=re.IGNORECASE):
            fail(f"secret-like assignment appears in R5 scope: {pattern}")
    ok("no SSH automation, execution implementation, or real secret assignments exist in R5 scope")

    # This task should only introduce R5 files and local release index updates.
    # Full git diff inspection remains a shell-level check; validator validates R5 scope.
    ok("R5 remains entry-gate-only and does not define execution behavior")
    print(PASS)

if __name__ == "__main__":
    main()
