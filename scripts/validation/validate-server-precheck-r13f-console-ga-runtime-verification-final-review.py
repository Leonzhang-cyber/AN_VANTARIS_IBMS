#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13F.md"
PACK_DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW.md"
FINAL_NOTE = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13F_FINAL_VERIFICATION_NOTE.md"
REG = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13f/server-precheck-r13f.registry.json"
EVID = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13f/server-precheck-r13f.evidence.json"
VAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13f/server-precheck-r13f.validation.json"
FINAL = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r13f/server-precheck-r13f.final-verification.json"
INDEX = ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md"

SOURCE_DOCS = [
    (ROOT / "AN_VANTARIS_ONE/MENU_GA_R1.md", "ONE_MENU_GA_R1_INTERNATIONAL_L1_L2_L3_MENU_ARCHITECTURE_PASS"),
    (ROOT / "AN_VANTARIS_ONE/MENU_GA_R2.md", "ONE_MENU_GA_R2_ROUTE_COVERAGE_SIDEBAR_L3_BEHAVIOR_AUDIT_PASS"),
    (ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R13.md", "ONE_SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION_PASS"),
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
    "menuImplementationMutationPerformed",
    "serverMutationPerformed",
    "productionConfigMutationPerformed",
]

BRAND_TRUE_FIELDS = [
    "brandNamingReviewed",
    "brandPlacementReviewed",
    "businessDomainMenuGroupingPreserved",
    "vantarisOneBrandCovered",
    "vantarisConsoleCovered",
    "vantarisLinkCovered",
    "vantarisEdgeCovered",
    "vantarisCodeCovered",
    "vantarisDbCovered",
    "vantarisNexusAiCovered",
]

IBMS_TRUE_FIELDS = [
    "coverageReviewed",
    "domainMappingReviewed",
    "flatL1DumpAvoided",
    "operationsCovered",
    "sitesSpacesCovered",
    "systemsDevicesCovered",
    "alarmsEventsCovered",
    "faultManagementCovered",
    "maintenanceCovered",
    "energySustainabilityCovered",
    "facilityServicesCovered",
    "dataCenterOperationsCovered",
    "decisionEvidenceCovered",
    "commandCenterCovered",
    "intelligenceCovered",
    "aiVideoAnalyticsCovered",
    "digitalTwinCovered",
    "reportsCovered",
    "trustIdentityCovered",
    "administrationCovered",
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


def expect_true(obj, field):
    if obj.get(field) is not True:
        fail(f"{field} must be true")


def expect_false(obj, field):
    if obj.get(field) is not False:
        fail(f"{field} must be false")


def expect_pass(obj, name):
    if obj.get("status") != "PASS":
        fail(f"{name}.status must be PASS")


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
    ok("no executable server or runtime operation steps found")


def main():
    required_files = [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX, Path(__file__)]
    for path in required_files:
        if not path.exists():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    ok("R13F documents, registry, evidence, validation, final verification, release index, and validator exist")

    for path in [DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL, INDEX]:
        if PASS not in read(path):
            fail(f"PASS marker missing from {path.relative_to(ROOT)}")
    ok("R13F PASS marker exists in document, pack, registry, evidence, validation, final verification, and release index")

    reg = load_json(REG)
    evid = load_json(EVID)
    val = load_json(VAL)
    final = load_json(FINAL)

    if reg.get("taskId") != "SERVER-PRECHECK-R13F":
        fail("registry taskId is not SERVER-PRECHECK-R13F")
    if reg.get("stage") != "SERVER-PRECHECK-R13F":
        fail("registry stage is not SERVER-PRECHECK-R13F")
    if val.get("passMarker") != PASS or final.get("passMarker") != PASS:
        fail("validation or final verification pass marker mismatch")
    ok("registry, validation, and final verification markers are correct")

    expected_refs = {
        "stage": "SERVER-PRECHECK-R13F",
        "consoleRuntimeVerificationReference": "SERVER-PRECHECK-R13",
        "menuArchitectureBaselineReference": "MENU-GA-R1/R2",
        "deploymentExecutionApprovalReference": "SERVER-PRECHECK-R14",
    }
    for key, value in expected_refs.items():
        if evid.get(key) != value:
            fail(f"{key} must be {value}")
    ok("R13F evidence references MENU-GA-R1/R2, R13, and R14")

    dependency = evid.get("r14fDependency", {})
    for field in ["requiredBeforeR14fGo", "r13Completed", "r13fCompleted", "r14CanBeReevaluatedAfterR13f"]:
        expect_true(dependency, field)
    if dependency.get("r13DecisionBeforeFinalReview") != "HOLD":
        fail("r13DecisionBeforeFinalReview must be HOLD")
    ok("R14F dependency fields are correct")

    for key in FALSE_FLAGS:
        expect_false(evid, key)
    ok("runtime, production access, SSH, connection, build, mutation, and config flags are false")

    sidebar = evid.get("sidebarCollapseExpandFinalReview", {})
    for field in ["collapseControlPresent", "collapseExpandBehaviorReviewed", "l1L2VisibilityRulesPreserved", "l3RemainsOutsideSidebarAfterCollapseExpand"]:
        expect_true(sidebar, field)
    expect_pass(sidebar, "sidebarCollapseExpandFinalReview")
    ok("Sidebar collapse / expand final review is PASS")

    route = evid.get("routePageAvailabilityFinalReview", {})
    if route.get("routeCoverageAuditReference") != "MENU-GA-R2":
        fail("routeCoverageAuditReference must be MENU-GA-R2")
    for field in [
        "allVisibleRoutesHavePageOrGaCompliantPlaceholder",
        "duplicateRouteAuditPassed",
        "duplicateMenuAuditPassed",
        "noVisibleRouteBrokenPageStateRecorded",
    ]:
        expect_true(route, field)
    expect_pass(route, "routePageAvailabilityFinalReview")
    ok("Route and page availability final review is PASS")

    brand = evid.get("internationalBrandMenuFinalReview", {})
    for field in BRAND_TRUE_FIELDS:
        expect_true(brand, field)
    expect_pass(brand, "internationalBrandMenuFinalReview")
    ok("International brand menu final review is PASS")

    ibms = evid.get("ibmsUpgradedMenuFinalReview", {})
    for field in IBMS_TRUE_FIELDS:
        expect_true(ibms, field)
    expect_pass(ibms, "ibmsUpgradedMenuFinalReview")
    ok("IBMS upgraded menu final review is PASS")

    role = evid.get("roleBasedVisibilityFinalReview", {})
    for field in ["customerRoleReviewed", "engineerRoleReviewed", "adminRoleReviewed"]:
        expect_true(role, field)
    for field in [
        "roleBoundaryViolationsDetected",
        "restrictedDeploymentContentExposedToCustomer",
        "restrictedEvidenceContentExposedToCustomer",
    ]:
        expect_false(role, field)
    expect_pass(role, "roleBasedVisibilityFinalReview")
    ok("Role-based visibility final review is PASS")

    forbidden = evid.get("forbiddenLanguageFinalReview", {})
    for field in [
        "mockDetectedInGaVisibleText",
        "demoDetectedInGaVisibleText",
        "pilotDetectedInGaVisibleText",
        "comingSoonDetectedInGaVisibleText",
    ]:
        expect_false(forbidden, field)
    expect_pass(forbidden, "forbiddenLanguageFinalReview")
    ok("Forbidden language final review is PASS")

    restricted = evid.get("restrictedEvidenceHandlingFinalReview", {})
    for field in [
        "productionScreenshotsStoredInPublicPacket",
        "customerHostnamesStoredInPublicPacket",
        "privateIpStoredInPublicPacket",
        "usernamesStoredInPublicPacket",
        "emailsStoredInPublicPacket",
    ]:
        expect_false(restricted, field)
    expect_true(restricted, "restrictedEvidenceReferenceOnly")
    expect_pass(restricted, "restrictedEvidenceHandlingFinalReview")
    ok("Restricted evidence handling final review is PASS")

    decision = evid.get("runtimeVerificationFinalDecision")
    if decision not in ["HOLD", "GO", "NO-GO"]:
        fail("runtimeVerificationFinalDecision must be HOLD / GO / NO-GO")
    if decision != "GO":
        fail("runtimeVerificationFinalDecision must be GO for R13 HOLD closure")
    if evid.get("reviewer", {}).get("reviewStatus") != "ACCEPTED":
        fail("reviewer reviewStatus must be ACCEPTED")
    if evid.get("approver", {}).get("approvalStatus") != "GO":
        fail("approver approvalStatus must be GO")
    if final.get("r13HoldClosureStatus") != "COMPLETE":
        fail("final r13HoldClosureStatus must be COMPLETE")
    if final.get("runtimeVerificationFinalDecision") != "GO":
        fail("final runtimeVerificationFinalDecision must be GO")
    ok("R13 HOLD closure and runtimeVerificationFinalDecision are GO")

    for key, value in reg.get("boundaries", {}).items():
        if value is not False:
            fail(f"registry boundary must be false: {key}")
    ok("registry boundaries are false")

    for path, marker in SOURCE_DOCS:
        if marker not in read(path):
            fail(f"missing source marker {marker} in {path.relative_to(ROOT)}")
    ok("MENU-GA-R1/R2, R13, and R14 source markers exist")

    check_no_executable_steps([DOC, PACK_DOC, FINAL_NOTE, REG, EVID, VAL, FINAL])

    ok("SERVER-PRECHECK-R13F Console GA Runtime Verification Final Review validation complete")
    print(PASS)


if __name__ == "__main__":
    main()
