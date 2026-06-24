#!/usr/bin/env python3
"""Validate SERVER-PRECHECK-R6 manual read-only observation command pack."""

from __future__ import annotations

import json
import re
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS"

DOC = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6.md"
COMMAND_PACK = ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R6_MANUAL_READONLY_COMMAND_PACK.md"
REGISTRY = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r6/server-precheck-r6.registry.json"
EVIDENCE = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r6/server-precheck-r6.evidence.json"
VALIDATION = ROOT / "AN_VANTARIS_ONE/registries/server-precheck-r6/server-precheck-r6.validation.json"

SOURCE_MARKERS = {
    "r4": (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4.md",
        "ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS",
    ),
    "r4f": (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R4_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R4F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
    "r5": (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5.md",
        "ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS",
    ),
    "r5f": (
        ROOT / "AN_VANTARIS_ONE/SERVER_PRECHECK_R5_FINAL_VERIFICATION_NOTE.md",
        "ONE_SERVER_PRECHECK_R5F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS",
    ),
}

ALLOWED_TEMPLATES = [
    "hostname",
    "whoami",
    "date",
    "uptime",
    "uname -a",
    "cat /etc/os-release",
    "df -h",
    "free -h",
    "ps aux",
    "systemctl status <APPROVED_SERVICE> --no-pager",
    "journalctl -u <APPROVED_LOG_UNIT> --no-pager -n 100",
    "ls -al <APPROVED_PATH>",
    "find <APPROVED_PATH> -maxdepth 2 -type f",
    "cat <APPROVED_NON_SECRET_FILE>",
    "ss -tulpen",
]

FALSE_BOUNDARIES = [
    "sshExecutionAllowed",
    "sshConnectionCommandsIncluded",
    "executableShellScriptCreated",
    "frontendCreated",
    "backendCreated",
    "routesCreated",
    "deploymentAllowed",
    "installAllowed",
    "dbMutationAllowed",
    "authMutationAllowed",
    "runtimeActionAllowed",
    "secretsHandlingAllowed",
    "menuGaR1R2MutationAllowed",
    "serverPrecheckR4R5MutationAllowed",
]

EXECUTABLE_FENCE_LANGS = {"", "sh", "bash", "zsh", "shell", "console", "terminal"}
FORBIDDEN_EXEC_RE = re.compile(
    r"(^|\s)(ssh|scp|rsync|sudo)\b|"
    r"\bsystemctl\s+(restart|stop|start)\b|"
    r"(^|\s)(restart|stop|start|install)\b",
    re.IGNORECASE,
)
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"\b(password|token|secret|private[_ -]?key|credential)\b\s*[:=]\s*(['\"])[^'\"]+\2",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def assert_pass_marker(path: Path) -> None:
    if PASS_MARKER not in read_text(path):
        fail(f"PASS marker missing in {path.relative_to(ROOT)}")


def fenced_blocks(markdown: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_block = False
    lang = ""
    body: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("```"):
            if not in_block:
                in_block = True
                lang = line[3:].strip().split()[0].lower() if line[3:].strip() else ""
                body = []
            else:
                blocks.append((lang, "\n".join(body)))
                in_block = False
                lang = ""
                body = []
            continue
        if in_block:
            body.append(line)

    if in_block:
        fail("unterminated fenced block in command pack")
    return blocks


def assert_no_executable_command_blocks(command_pack_text: str) -> None:
    for lang, body in fenced_blocks(command_pack_text):
        if lang in EXECUTABLE_FENCE_LANGS:
            fail(f"executable command fence is not allowed: {lang or '<empty>'}")
        if lang in EXECUTABLE_FENCE_LANGS and FORBIDDEN_EXEC_RE.search(body):
            fail("forbidden command found in executable command block")


def assert_no_credential_assignments(path: Path) -> None:
    text = read_text(path)
    if CREDENTIAL_ASSIGNMENT_RE.search(text):
        fail(f"credential-like assignment found in {path.relative_to(ROOT)}")


def main() -> None:
    required_files = [
        DOC,
        COMMAND_PACK,
        REGISTRY,
        EVIDENCE,
        VALIDATION,
        Path(__file__).resolve(),
    ]
    for path in required_files:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    for path in [DOC, COMMAND_PACK, REGISTRY, EVIDENCE, VALIDATION]:
        assert_pass_marker(path)
        assert_no_credential_assignments(path)

    registry = load_json(REGISTRY)
    load_json(EVIDENCE)
    load_json(VALIDATION)

    for key in FALSE_BOUNDARIES:
        if registry.get(key) is not False:
            fail(f"registry boundary must be false: {key}")
    if registry.get("manualApprovalRequiredBeforeUse") is not True:
        fail("manualApprovalRequiredBeforeUse must be true")
    if registry.get("passMarker") != PASS_MARKER:
        fail("registry passMarker mismatch")
    if registry.get("reviewedReadOnlyTemplates") != ALLOWED_TEMPLATES:
        fail("reviewedReadOnlyTemplates do not match approved R6 list")

    if COMMAND_PACK.suffix != ".md":
        fail("command pack must be markdown")
    mode = COMMAND_PACK.stat().st_mode
    if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        fail("command pack must not be executable")

    command_pack_text = read_text(COMMAND_PACK)
    if command_pack_text.startswith("#!"):
        fail("command pack must not include a shebang")
    for template in ALLOWED_TEMPLATES:
        if template not in command_pack_text:
            fail(f"approved template missing from command pack: {template}")
    assert_no_executable_command_blocks(command_pack_text)

    registry_markers = registry.get("sourceMarkers", {})
    for key, (path, marker) in SOURCE_MARKERS.items():
        if registry_markers.get(key) != marker:
            fail(f"registry source marker mismatch: {key}")
        if marker not in read_text(path):
            fail(f"source marker missing: {marker}")

    print("SERVER-PRECHECK-R6 validation PASS")
    print(PASS_MARKER)


if __name__ == "__main__":
    main()
