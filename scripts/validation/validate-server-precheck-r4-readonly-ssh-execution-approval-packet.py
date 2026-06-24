#!/usr/bin/env python3
"""Validate SERVER-PRECHECK-R4 read-only SSH execution approval packet."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PASS = "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r4/server-precheck-r4.registry.json"
EVIDENCE = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r4/server-precheck-r4.evidence.json"
VALIDATION = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r4/server-precheck-r4.validation.json"
VALIDATOR = ROOT / "scripts/validation/validate-server-precheck-r4-readonly-ssh-execution-approval-packet.py"

OPTIONAL_R4_CODE_PATHS = [
    ROOT / "AN_VANTARIS_IBMS-backend/src/api/server_ssh_approval_packet",
    ROOT / "AN_VANTARIS_IBMS-backend/src/server_ssh_approval_packet",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/modules/server/ServerSshApprovalPacket.vue",
    ROOT / "AN_VANTARIS_IBMS-frontend/src/services/api/serverSshApprovalPacket.ts",
]

FLAGS = {
    "sshExecutionAllowed": False,
    "deploymentAllowed": False,
    "installAllowed": False,
    "dbMutationAllowed": False,
    "authMutationAllowed": False,
    "secretsMutationAllowed": False,
    "runtimeActionAllowed": False,
    "approvalRequiredBeforeAnySsh": True,
    "humanApprovalRequired": True,
}

REQUIRED_WHITELIST = {
    "hostname",
    "whoami",
    "date",
    "uptime",
    "uname -a",
    "df -h",
    "free -h",
    "ps aux",
    "systemctl status <approved-service>",
    "journalctl -u <approved-service> --no-pager -n 100",
    "ls -al <approved-path>",
    "cat <approved-non-secret-file>",
    "find <approved-path> -maxdepth 2 -type f",
}

REQUIRED_BLACKLIST = {
    "sudo",
    "su",
    "chmod",
    "chown",
    "rm",
    "mv",
    "cp",
    "mkdir",
    "touch",
    "vi",
    "vim",
    "nano",
    "systemctl restart",
    "systemctl stop",
    "systemctl start",
    "systemctl enable",
    "systemctl disable",
    "service restart",
    "kill",
    "pkill",
    "docker",
    "docker compose",
    "kubectl",
    "npm install",
    "pip install",
    "apt",
    "yum",
    "dnf",
    "systemctl edit",
    "crontab",
    "psql write operations",
    "mysql write operations",
    "any command containing password/token/secret/private key output",
}

FORBIDDEN_CODE_TOKENS = [
    "import sub" + "process",
    "os." + "system",
    "para" + "miko",
    "fabric",
    "ssh.exec",
    "ssh_client",
    "methods=[\"POST\"]",
    "methods=[\"PUT\"]",
    "methods=[\"PATCH\"]",
    "methods=[\"DELETE\"]",
]

SECRET_ASSIGNMENT_PATTERNS = [
    re.compile(r"(?i)(password|token|secret|private_key)\s*[:=]\s*['\"][^'\"<>]{8,}['\"]"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(read(path))
    if not isinstance(payload, dict):
        fail(f"JSON root must be object: {path.relative_to(ROOT)}")
    return payload


def main() -> int:
    for path in [DOC, REGISTRY, EVIDENCE, VALIDATION, VALIDATOR]:
        if not path.exists():
            fail(f"missing required R4 file: {path.relative_to(ROOT)}")
    ok("required R4 document, registry, evidence, validation, and validator files exist")

    registry = load_json(REGISTRY)
    evidence = load_json(EVIDENCE)
    validation = load_json(VALIDATION)
    for name, payload in (("registry", registry), ("evidence", evidence), ("validation", validation)):
        if PASS not in json.dumps(payload):
            fail(f"PASS marker missing in {name}")
    if PASS not in read(DOC):
        fail("PASS marker missing in document")
    ok("R4 PASS marker exists in document and JSON registries")

    if registry.get("taskId") != "SERVER-PRECHECK-R4":
        fail("registry taskId must be SERVER-PRECHECK-R4")
    if registry.get("mode") != "read-only approval packet":
        fail("registry mode must be read-only approval packet")
    for key, expected in FLAGS.items():
        if registry.get(key) is not expected:
            fail(f"registry {key} must be {expected}")
    ok("registry boundary flags are correct")

    whitelist = set(map(str, registry.get("commandWhitelist", [])))
    blacklist = set(map(str, registry.get("commandBlacklist", [])))
    if not REQUIRED_WHITELIST.issubset(whitelist):
        fail(f"command whitelist missing required read-only commands: {sorted(REQUIRED_WHITELIST - whitelist)}")
    if not REQUIRED_BLACKLIST.issubset(blacklist):
        fail(f"command blacklist missing required dangerous commands: {sorted(REQUIRED_BLACKLIST - blacklist)}")
    if any(command in blacklist for command in whitelist):
        fail("whitelist and blacklist overlap")
    ok("command whitelist and dangerous-command blacklist are present")

    if not registry.get("stopConditions"):
        fail("stopConditions must exist")
    if not registry.get("evidenceChecklist"):
        fail("evidenceChecklist must exist")
    if not registry.get("redactionPolicy"):
        fail("redactionPolicy must exist")
    ok("stop conditions, evidence checklist, and redaction policy exist")

    combined = "\n".join(read(path) for path in [DOC, REGISTRY, EVIDENCE, VALIDATION, VALIDATOR])
    for pattern in SECRET_ASSIGNMENT_PATTERNS:
        if pattern.search(combined):
            fail("secret-like credential assignment or private key material found")
    ok("no real secrets, credentials, tokens, or private keys are present")

    code_scope = []
    for path in OPTIONAL_R4_CODE_PATHS:
        if path.is_dir():
            code_scope.extend(file for file in path.rglob("*") if file.is_file())
        elif path.exists():
            code_scope.append(path)
    code_text = "\n".join(read(path) for path in code_scope)
    lowered_code = code_text.lower()
    for token in FORBIDDEN_CODE_TOKENS:
        if token in lowered_code:
            fail(f"forbidden SSH/runtime implementation token found in optional R4 code scope: {token}")
    ok("no subprocess, SSH library, shell execution, or write endpoint exists in R4 code scope")

    menu_paths = [
        ROOT / "AN_VANTARIS_ONE/MENU_GA_R1.md",
        ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.registry.json",
        ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.evidence.json",
        ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.validation.json",
        ROOT / "AN_VANTARIS_ONE/registries/menu-ga-r1/menu-ga-r1.final-verification.json",
    ]
    if any("SERVER_PRECHECK_R4" in read(path) for path in menu_paths if path.exists()):
        fail("MENU-GA-R1 files must not be modified for SERVER-PRECHECK-R4 scope")
    ok("MENU-GA-R1 files are not part of R4 scope")

    print(PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
