#!/usr/bin/env python3
"""Static Flask route vs OpenAPI path comparison (stdlib only).

Does not import Flask, start services, or connect to a database.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROUTE_DECORATOR_RE = re.compile(
    r"@\s*[\w.]+\.route\(\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)

# OpenAPI / YAML path keys at line start (indented), e.g. "  /system/menus:"
OPENAPI_PATH_RE = re.compile(
    r"^\s*(/[\w\-./{}<>:_]+)\s*:\s*$",
    re.MULTILINE,
)

FLASK_PARAM_RE = re.compile(
    r"<(?:\w+:)?([\w_]+)>",
)


def normalize_flask_path(path: str) -> str:
    """Convert Flask path params to OpenAPI-style {param}."""
    normalized = FLASK_PARAM_RE.sub(r"{\1}", path)
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    # Collapse duplicate slashes
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.rstrip("/") or "/"


def normalize_openapi_path(path: str) -> str:
    normalized = path.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.rstrip("/") or "/"


def scan_flask_routes(api_root: Path) -> set[str]:
    routes: set[str] = set()
    if not api_root.exists():
        raise FileNotFoundError(f"Backend API root not found: {api_root}")

    for py_file in sorted(api_root.rglob("*.py")):
        try:
            text = py_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARN: could not read {py_file}: {exc}", file=sys.stderr)
            continue
        for match in ROUTE_DECORATOR_RE.finditer(text):
            routes.add(normalize_flask_path(match.group(1)))
    return routes


def scan_openapi_paths(openapi_dir: Path) -> dict[str, set[str]]:
    by_file: dict[str, set[str]] = {}
    if not openapi_dir.exists():
        raise FileNotFoundError(f"OpenAPI dir not found: {openapi_dir}")

    for yaml_file in sorted(openapi_dir.glob("*.yaml")):
        try:
            text = yaml_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARN: could not read {yaml_file}: {exc}", file=sys.stderr)
            continue
        paths = {
            normalize_openapi_path(match.group(1))
            for match in OPENAPI_PATH_RE.finditer(text)
        }
        by_file[yaml_file.name] = paths
    return by_file


def param_signature(path: str) -> str:
    """Signature ignoring param names: /iot/{x}/command -> /iot/{}/command"""
    return re.sub(r"\{[^}]+\}", "{}", path)


def paths_match(a: str, b: str) -> bool:
    if a == b:
        return True
    return param_signature(a) == param_signature(b)


def find_missing_in_openapi(backend: set[str], openapi_union: set[str]) -> list[str]:
    missing: list[str] = []
    for route in sorted(backend):
        if any(paths_match(route, oa) for oa in openapi_union):
            continue
        missing.append(route)
    return missing


def find_extra_in_openapi(backend: set[str], openapi_union: set[str]) -> list[str]:
    extra: list[str] = []
    for oa in sorted(openapi_union):
        if any(paths_match(oa, br) for br in backend):
            continue
        extra.append(oa)
    return extra


def print_report(
    backend_routes: set[str],
    openapi_by_file: dict[str, set[str]],
) -> None:
    openapi_union: set[str] = set()
    for paths in openapi_by_file.values():
        openapi_union |= paths

    missing = find_missing_in_openapi(backend_routes, openapi_union)
    extra = find_extra_in_openapi(backend_routes, openapi_union)

    print("=" * 72)
    print("IBMS Flask vs OpenAPI Static Route Validation")
    print("=" * 72)
    print(f"Backend routes (static scan): {len(backend_routes)}")
    print(f"OpenAPI paths (all yaml):       {len(openapi_union)}")
    for name, paths in openapi_by_file.items():
        print(f"  - {name}: {len(paths)} paths")
    print()

    print(f"Likely missing in OpenAPI ({len(missing)}):")
    for path in missing:
        print(f"  - {path}")
    print()

    print(f"OpenAPI paths not found in Flask scan ({len(extra)}):")
    for path in extra:
        print(f"  - {path}")
    print()

    print("Note: contract-only paths (e.g. /system/menu) may appear as extras.")
    print("Param naming differences (<device_code> vs {device_did}) are normalized.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Flask @route paths with OpenAPI yaml paths (static scan).",
    )
    parser.add_argument(
        "--backend-root",
        default="AN_VANTARIS_IBMS-backend/src/api",
        help="Root directory for Flask API modules",
    )
    parser.add_argument(
        "--openapi-dir",
        default="contracts/openapi",
        help="Directory containing OpenAPI yaml files",
    )
    args = parser.parse_args()

    backend_root = Path(args.backend_root)
    openapi_dir = Path(args.openapi_dir)

    try:
        backend_routes = scan_flask_routes(backend_root)
        openapi_by_file = scan_openapi_paths(openapi_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_report(backend_routes, openapi_by_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
