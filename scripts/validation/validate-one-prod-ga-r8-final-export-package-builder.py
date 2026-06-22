#!/usr/bin/env python3
"""Validate ONE-PROD-GA-R8 final export package builder."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
EXPORT_BASE = Path.home() / "Desktop/VANTARIS_FINAL_EXPORT"
EXPORT_NAME = "VANTARIS_ONE_PROD_GA_FOUNDATION_PACKAGES_R7_20260622"
EXPORT_STAGE = EXPORT_BASE / EXPORT_NAME
TARBALL = EXPORT_BASE / f"{EXPORT_NAME}.tar.gz"
SHA_FILE = Path(f"{TARBALL}.sha256")
REPORT = ROOT / "ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_REPORT.md"
PASS_MARKER = "ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_PASS"

ALLOWED_DIRTY = {
    "ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_REPORT.md",
    "scripts/validation/validate-one-prod-ga-r8-final-export-package-builder.py",
}

FORBIDDEN_PARTS = {
    ".git",
    ".env",
    "node_modules",
    "dist",
    "build",
    ".runtime",
    "__pycache__",
    ".DS_Store",
}
FORBIDDEN_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".crt",
}

REQUIRED_TARBALL_PATHS = [
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE/src/runtime/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE/src/product-runtime/edge/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_LINK/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_DB/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/deployment/prod-ga/offline-package/",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/ONE_PROD_GA_R7_FINAL_FOUNDATION_PACKAGE_CONSOLIDATED_RELEASE_INDEX.md",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/AN_VANTARIS_ONE/registries/prod-ga-final-foundation-package-consolidated-release-index.v1.json",
    f"{EXPORT_NAME}/AN_VANTARIS_IBMS/ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_REPORT.md",
    f"{EXPORT_NAME}/EXPORT_METADATA/export-manifest.v1.json",
    f"{EXPORT_NAME}/EXPORT_METADATA/RESTORE_AND_VERIFY_README.md",
]

PROHIBITED_CLAIMS = [
    "install executed: true",
    "rollback executed: true",
    "db migration executed: true",
    "runtime executed: true",
    "runtime activation: true",
]


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    suffix = f" - {details}" if details else ""
    print(f"[{status}] {name}{suffix}")
    return condition


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha_file_value() -> str:
    if not SHA_FILE.is_file():
        return ""
    return SHA_FILE.read_text(encoding="utf-8").split()[0].strip()


def is_forbidden_path(path: Path) -> bool:
    name = path.name
    if name in FORBIDDEN_PARTS or name.startswith(".env.") or name.startswith("._"):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def staging_forbidden_scan() -> list[str]:
    if not EXPORT_STAGE.is_dir():
        return []
    matches: list[str] = []
    for path in EXPORT_STAGE.rglob("*"):
        if is_forbidden_path(path):
            matches.append(path.relative_to(EXPORT_STAGE).as_posix())
    return sorted(matches)


def tar_names() -> list[str]:
    with tarfile.open(TARBALL, "r:gz") as archive:
        return archive.getnames()


def tar_forbidden(names: list[str]) -> list[str]:
    matches: list[str] = []
    for name in names:
        parts = Path(name).parts
        basename = parts[-1] if parts else name
        if any(part in FORBIDDEN_PARTS for part in parts):
            matches.append(name)
            continue
        if basename.startswith(".env.") or basename.startswith("._") or Path(basename).suffix in FORBIDDEN_SUFFIXES:
            matches.append(name)
    return sorted(matches)


def tar_contains(names: list[str], expected: str) -> bool:
    normalized = expected.rstrip("/")
    return any(name == normalized or name.startswith(normalized + "/") for name in names)


def git_dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=False)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line:
            continue
        paths.add(line[3:])
    return paths


def main() -> int:
    checks: list[bool] = []
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""

    checks.append(check("R8 report exists", REPORT.is_file()))
    checks.append(check("PASS marker exists in R8 report", PASS_MARKER in report_text))
    checks.append(check("Export tarball exists", TARBALL.is_file(), str(TARBALL)))
    checks.append(check("SHA256 file exists", SHA_FILE.is_file(), str(SHA_FILE)))

    actual_sha = sha256(TARBALL) if TARBALL.is_file() else ""
    expected_sha = sha_file_value()
    checks.append(check("SHA256 verifies against tarball", actual_sha == expected_sha and bool(actual_sha), actual_sha))
    checks.append(check("R8 report includes final SHA256 value", actual_sha in report_text))

    if EXPORT_STAGE.exists():
        checks.append(check("Export manifest exists in staging", (EXPORT_STAGE / "EXPORT_METADATA/export-manifest.v1.json").is_file()))
        checks.append(check("Restore README exists in staging", (EXPORT_STAGE / "EXPORT_METADATA/RESTORE_AND_VERIFY_README.md").is_file()))
        staging_matches = staging_forbidden_scan()
        checks.append(check("Staging forbidden scan empty", not staging_matches, ", ".join(staging_matches[:10])))

    names = tar_names() if TARBALL.is_file() else []
    tar_matches = tar_forbidden(names)
    checks.append(check("Tarball forbidden scan empty", not tar_matches, ", ".join(tar_matches[:10])))
    for expected_path in REQUIRED_TARBALL_PATHS:
        checks.append(check(f"Tarball contains {expected_path}", tar_contains(names, expected_path)))

    dirty = git_dirty_paths()
    checks.append(check("Current repository clean except R8 report/validator before commit", dirty.issubset(ALLOWED_DIRTY), str(sorted(dirty))))

    lower_report = report_text.lower()
    checks.append(check("No install/rollback/DB/runtime execution claim", not any(claim in lower_report for claim in PROHIBITED_CLAIMS)))

    if all(checks):
        print(PASS_MARKER)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

