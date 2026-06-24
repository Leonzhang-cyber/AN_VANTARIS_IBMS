#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13/server-precheck-r13.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13/server-precheck-r13.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13/server-precheck-r13.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13/server-precheck-r13.final-verification.json"
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
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R11.md", "ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R12.md", "ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R14.md", "ONE_SERVER_PRECHECK_R14_APP_DB_DEPLOYMENT_EXECUTION_APPROVAL_GATE_PASS"),
]

FALSE_FLAGS = [
    "runtimeVerificationPerformedByThisPacket",
    "productionServerAccessPerformed",
    "sshExecutedByThisPacket",
    "appServerConnectionPerformed",
    "dbServerConnectionPerformed",
    "buildPerformed",
    "npmNodeCommandExecuted",
    "frontendBackendMutationPerformed",
    "routeMutationPerformed",
    "serverMutationPerformed",
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
    r"\bpm2\s+start\b",
    r"\bpm2\s+restart\b",
    r"\bpm2\s+reload\b",
    r"\bpython\s+app\.py\b",
    r"\bflask\s+run\b",
    r"\bgunicorn\b",
    r"\bnode\s+server\.js\b",
    r"\bprisma\s+migrate\b",
    r"(^|\s)psql\b",
    r"(^|\s)pg_dump\b",
    r"(^|\s)pg_restore\b",
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
    executable_scope = []
    for path in paths:
        for lang, body in fenced_blocks(read(path)):
            if lang in EXECUTABLE_LANGS:
                executable_scope.append((path, body))
    for path, body in executable_scope:
        for pattern in FORBIDDEN_EXEC_PATTERNS:
            if re.search(pattern, body, flags=re.IGNORECASE):
                fail(f"forbidden executable operation in {path.relative_to(ROOT)}: {pattern}")
    ok("no executable server or runtime operation steps found")


def main():
    required_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R13 documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R13 PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R13":
        fail("registry taskId is not SERVER-PRECHECK-R13")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R13",
        "menuArchitectureBaselineReference": "MENU-GA-R1/R2",
        "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
        "dbDeploymentPreparationReference": "SERVER-PRECHECK-R11",
        "appDeploymentPreparationReference": "SERVER-PRECHECK-R12",
        "deploymentExecutionApprovalReference": "SERVER-PRECHECK-R14",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("evidence stage and MENU-GA-R1/R2, R10, R11, R12, and R14 references are correct")

    closure = evid.get("r14DependencyClosure", {})
    if closure.get("requiredByR14") is not True:
        fail("r14DependencyClosure.requiredByR14 must be true")
    if closure.get("r13Completed") is not True:
        fail("r14DependencyClosure.r13Completed must be true")
    if closure.get("r14CanBeReevaluatedAfterR13") is not True:
        fail("r14DependencyClosure.r14CanBeReevaluatedAfterR13 must be true")
    if closure.get("r14DecisionBeforeR13") != "HOLD":
        fail("r14DecisionBeforeR13 must be HOLD")
    ok("R14 dependency closure is recorded")

    for key in FALSE_FLAGS:
        if evid.get(key) is not False:
            fail(f"{key} must be false")
    ok("runtime, production access, SSH, connection, build, mutation, and config flags are false")

    if evid.get("dashboardNaming", {}).get("dashboardUsedAsPrimaryL1") is not True:
        fail("dashboardUsedAsPrimaryL1 must be true")
    if evid.get("dashboardNaming", {}).get("homeUsedAsPrimaryL1") is not False:
        fail("homeUsedAsPrimaryL1 must be false")
    ok("Dashboard naming verification is correct")

    sidebar = evid.get("sidebarL1L2", {})
    if sidebar.get("l1DisplayedInSidebar") is not True:
        fail("l1DisplayedInSidebar must be true")
    if sidebar.get("l2DisplayedInSidebar") is not True:
        fail("l2DisplayedInSidebar must be true")
    if sidebar.get("l3ExcludedFromSidebar") is not True:
        fail("l3ExcludedFromSidebar must be true")
    l3 = evid.get("l3ContentAreaNavigation", {})
    if l3.get("l3DisplayedInContentAreaTop") is not True:
        fail("l3DisplayedInContentAreaTop must be true")
    if l3.get("l3SharesSamePageLayout") is not True:
        fail("l3SharesSamePageLayout must be true")
    if l3.get("l3NotRenderedAsSidebarItems") is not True:
        fail("l3NotRenderedAsSidebarItems must be true")
    ok("Sidebar L1/L2 and L3 content-area verification are correct")

    forbidden = evid.get("forbiddenLanguageScan", {})
    for key in ["mockDetected", "demoDetected", "pilotDetected", "comingSoonDetected"]:
        if forbidden.get(key) is not False:
            fail(f"forbiddenLanguageScan.{key} must be false")
    restricted = evid.get("restrictedEvidenceHandling", {})
    for key in [
        "productionScreenshotsStoredInPublicPacket",
        "customerHostnamesStoredInPublicPacket",
        "privateIpStoredInPublicPacket",
        "usernamesStoredInPublicPacket",
    ]:
        if restricted.get(key) is not False:
            fail(f"restrictedEvidenceHandling.{key} must be false")
    if restricted.get("restrictedEvidenceReferenceOnly") is not True:
        fail("restrictedEvidenceReferenceOnly must be true")
    ok("forbidden language and restricted evidence flags are correct")

    if evid.get("runtimeVerificationDecision") not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeVerificationDecision must be HOLD / GO / NO-GO")
    if evid.get("reviewer", {}).get("reviewStatus") not in reg.get("allowedReviewStatuses", []):
        fail("reviewer reviewStatus is invalid")
    if evid.get("approver", {}).get("approvalStatus") not in reg.get("allowedApprovalStatuses", []):
        fail("approver approvalStatus is invalid")
    ok("runtime verification decision, reviewer, and approver models are correct")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("R1-R12 and R14 source markers exist")

    check_no_executable_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R13 Console International GA Menu Runtime Verification validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
