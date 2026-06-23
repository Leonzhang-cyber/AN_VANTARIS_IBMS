#!/usr/bin/env python3
"""Validate LOCAL-RELEASE-INDEX-R1 customer demo local increment index."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_LOCAL_RELEASE_INDEX_R1_CUSTOMER_DEMO_INCREMENT_PASS"

FILES = [
    ROOT / "AN_VANTARIS_ONE/LOCAL_RELEASE_INDEX_R1.md",
    ROOT / "AN_VANTARIS_ONE/registries/local-release-index-r1/local-release-index-r1.registry.json",
    ROOT / "AN_VANTARIS_ONE/registries/local-release-index-r1/local-release-index-r1.evidence.json",
    ROOT / "AN_VANTARIS_ONE/registries/local-release-index-r1/local-release-index-r1.validation.json",
]
COMMIT_HASHES = [
    "70fef5f1e2b27df0d5ce2fbdbf21cc4920b0e84d",
    "d2e1b6b72adb454338f0c1db6f39752ff19976c6",
    "7253e72ba8e3d7fd6c77d64dca26a2cfac69d21e",
    "6438d6b18bab4d343dc1a255b8b2d201b6422587",
]
LOCAL_TAGS = [
    "asset-context-ga-r1-unified-linkage-local-freeze-20260623",
    "code-ga-r1-policy-gate-preview-local-freeze-20260623",
    "nexusai-ga-r3-branch-diff-audit-local-freeze-20260623",
    "server-precheck-r1-dual-server-readonly-audit-local-freeze-20260623",
]
MARKERS = [
    "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS",
    "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS",
    "ONE_NEXUSAI_GA_R3_BRANCH_DIFF_AUDIT_PASS",
    "ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS",
]
BASELINE = "0ddf2a4c06fb5d50201b9b3936b85f4457c9c6c4"
CURRENT = "6438d6b18bab4d343dc1a255b8b2d201b6422587"
GUARDRAILS = [
    "read-only",
    "no push",
    "no SSH",
    "no deployment",
    "no DB write",
    "no runtime",
    "no EDGE/LINK command",
    "no device control",
    "no production activation",
]
FORBIDDEN = [
    "sub" + "process",
    "os." + "system",
    "req" + "uests",
    "so" + "cket",
    "para" + "miko",
    "psy" + "copg",
    "py" + "mysql",
    "sqlalchemy." + "create_engine",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def main() -> int:
    validator_path = ROOT / "scripts/validation/validate-local-release-index-r1-customer-demo-increment.py"
    for path in FILES + [validator_path]:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")
    ok("required local release index files exist")

    registry = json.loads(read(FILES[1]))
    evidence = json.loads(read(FILES[2]))
    validation = json.loads(read(FILES[3]))
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS_MARKER not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    if registry.get("scope") != "LOCAL_RELEASE_INDEX_R1":
        fail("registry scope invalid")
    if registry.get("remoteAligned") is not False or registry.get("pushExecuted") is not False:
        fail("registry remoteAligned/pushExecuted flags invalid")
    ok("registry/evidence/validation JSON parse and core flags are correct")

    combined = "\n".join(read(path) for path in FILES)
    for token in COMMIT_HASHES + LOCAL_TAGS + MARKERS + [BASELINE, CURRENT]:
        if token not in combined:
            fail(f"required release token missing: {token}")
    ok("commit hashes, local tags, validator markers, baseline, and current HEAD are present")

    for phrase in GUARDRAILS:
        if phrase not in combined:
            fail(f"required guardrail phrase missing: {phrase}")
    ok("required guardrail phrases are present")

    validator_text = read(validator_path)
    for token in FORBIDDEN:
        if token in validator_text:
            fail(f"forbidden executable token present in validator: {token}")
    ok("validator contains no forbidden executable tokens")

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
