#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PASS_MARKER = "ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_PASS"
CUSTOMER_DIR = ROOT / "deployment/prod-ga/customer-delivery"
PACKAGES_DIR = ROOT / "AN_VANTARIS_ONE/packages"

REQUIRED_FILES = [
    CUSTOMER_DIR / "README.md",
    CUSTOMER_DIR / "customer-delivery.manifest.v1.json",
    CUSTOMER_DIR / "scripts/precheck-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/install-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/verify-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/rollback-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/package-counts-customer-delivery.sh",
    CUSTOMER_DIR / "ui/ENGINEER_INSTALLER_CONSOLE_SPEC.md",
    CUSTOMER_DIR / "ui/CUSTOMER_DELIVERY_UI_FLOW.md",
    CUSTOMER_DIR / "checklists/CUSTOMER_GA_ACTIVATION_CHECKLIST.md",
    CUSTOMER_DIR / "checklists/OFFLINE_DEPLOYMENT_ACCEPTANCE_CHECKLIST.md",
    ROOT / "ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_REPORT.md",
    ROOT / "AN_VANTARIS_ONE/registries/prod-ga-final-customer-delivery-edition.v1.json",
]

SCRIPTS = [
    CUSTOMER_DIR / "scripts/precheck-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/install-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/verify-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/rollback-customer-delivery.sh",
    CUSTOMER_DIR / "scripts/package-counts-customer-delivery.sh",
]

EXPECTED_COUNTS = {
    "AN_VANTARIS_EDGE": 248,
    "AN_VANTARIS_LINK": 153,
    "AN_VANTARIS_DB": 14,
    "AN_VANTARIS_Contracts": 174,
}

FORBIDDEN_NAMES = {
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
    ".DS_Store",
}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".crt"}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_files(path: Path) -> int:
    return sum(1 for child in path.rglob("*") if child.is_file())


def load_json(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"JSON parse failed for {path}: {exc}")


def run_validator(path: Path, label: str) -> None:
    if not path.exists():
        ok(f"{label} validator not present; skipped")
        return
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    project_pythonpath = str(ROOT / "AN_VANTARIS_ONE")
    env["PYTHONPATH"] = (
        project_pythonpath
        if not existing_pythonpath
        else f"{project_pythonpath}{os.pathsep}{existing_pythonpath}"
    )
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        fail(f"{label} validator failed")
    ok(f"{label} validator passed")


def find_forbidden(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for base in paths:
        if not base.exists():
            continue
        for child in base.rglob("*"):
            name = child.name
            if (
                name in FORBIDDEN_NAMES
                or name.startswith(".env.")
                or name.startswith("._")
                or any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)
            ):
                hits.append(str(child.relative_to(ROOT)))
    return hits


def assert_pass_marker(path: Path) -> None:
    if PASS_MARKER not in read_text(path):
        fail(f"PASS marker missing from {path}")
    ok(f"PASS marker present in {path.relative_to(ROOT)}")


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"Required R9 file missing: {path}")
    ok("All R9 files exist")

    manifest_path = CUSTOMER_DIR / "customer-delivery.manifest.v1.json"
    registry_path = ROOT / "AN_VANTARIS_ONE/registries/prod-ga-final-customer-delivery-edition.v1.json"
    manifest = load_json(manifest_path)
    registry = load_json(registry_path)
    ok("Manifest and registry JSON parse")

    for path in [
        CUSTOMER_DIR / "README.md",
        ROOT / "ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_REPORT.md",
        manifest_path,
        registry_path,
    ]:
        assert_pass_marker(path)

    for script in SCRIPTS:
        mode = script.stat().st_mode
        if not mode & stat.S_IXUSR:
            fail(f"Script is not executable: {script}")
        text = read_text(script)
        if "set -euo pipefail" not in text:
            fail(f"Script missing set -euo pipefail: {script}")
        if "systemctl" in text or "npm install" in text or "prisma migrate" in text:
            fail(f"Script contains forbidden runtime/install command: {script}")
    ok("Scripts executable and shell safety header present")

    install_text = read_text(CUSTOMER_DIR / "scripts/install-customer-delivery.sh")
    rollback_text = read_text(CUSTOMER_DIR / "scripts/rollback-customer-delivery.sh")
    if "EXECUTE_NOT_IMPLEMENTED_IN_R9_SCAFFOLD" not in install_text:
        fail("Install script does not refuse --execute")
    if "EXECUTE_NOT_IMPLEMENTED_IN_R9_SCAFFOLD" not in rollback_text:
        fail("Rollback script does not refuse --execute")
    if "dry-run" not in install_text or "dry-run" not in rollback_text:
        fail("Install/rollback scripts do not document dry-run default")
    ok("Install and rollback scripts default to dry-run and refuse execution")

    for package_name, expected_count in EXPECTED_COUNTS.items():
        package_path = PACKAGES_DIR / package_name
        actual_count = count_files(package_path)
        if actual_count != expected_count:
            fail(f"{package_name} file count {actual_count} != {expected_count}")
    ok("Package counts match EDGE 248, LINK 153, DB 14, Contracts 174")

    forbidden = find_forbidden([PACKAGES_DIR, CUSTOMER_DIR])
    if forbidden:
        fail("Forbidden files found:\n" + "\n".join(forbidden))
    ok("Forbidden scan empty across packages and customer-delivery scaffold")

    for marker in [
        "ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_PASS",
        "ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX_PASS",
        "ONE_PROD_GA_R6_FULL_EDGE_RUNTIME_RESYNC_GATE_PASS",
    ]:
        result = subprocess.run(
            [
                "/usr/bin/grep",
                "-R",
                marker,
                str(ROOT),
                "--exclude-dir=.git",
                "--exclude-dir=node_modules",
                "--exclude-dir=.venv",
                "--exclude-dir=venv",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            fail(f"Prior PASS marker missing: {marker}")
    ok("R8/R7/R6 PASS markers exist")

    for data, label in [(manifest, "manifest"), (registry, "registry")]:
        if data.get("passMarker") != PASS_MARKER:
            fail(f"{label} passMarker mismatch")
        safety = data.get("safetyDefaults", {})
        expected_safety = {
            "dryRunDefault": True,
            "runtimeActivationDefault": False,
            "dbMigrationDefault": False,
            "destructiveRollbackDefault": False,
            "secretBundling": False,
        }
        for key, expected in expected_safety.items():
            if safety.get(key) is not expected:
                fail(f"{label} safetyDefaults.{key} expected {expected}")
        execution = data.get("executionStatus", {})
        for key in [
            "installExecuted",
            "rollbackExecuted",
            "dbMigrationExecuted",
            "runtimeActivated",
            "pushPerformed",
            "tagCreated",
            "mergePerformed",
            "rebasePerformed",
        ]:
            if execution.get(key) is not False:
                fail(f"{label} executionStatus.{key} must be false")
    ok("Manifest and registry safety/execution flags are correct")

    report_text = read_text(ROOT / "ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_REPORT.md")
    forbidden_claims = [
        "Install executed: true",
        "Rollback executed: true",
        "DB migration executed: true",
        "Runtime activation executed: true",
        "Push performed: true",
        "Tag created: true",
        "Main merge/rebase performed: true",
    ]
    for claim in forbidden_claims:
        if claim in report_text:
            fail(f"Forbidden execution claim in report: {claim}")
    ok("No install/rollback/DB/runtime/push/tag/merge/rebase execution claim")

    run_validator(ROOT / "scripts/validation/validate-one-package-route-enforcement.py", "Package route enforcement")
    run_validator(ROOT / "scripts/validation/validate-one-boundaries.py", "Boundary baseline")

    print(PASS_MARKER)


if __name__ == "__main__":
    main()
