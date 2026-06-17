#!/usr/bin/env python3
"""Static Flask route+method vs OpenAPI operation comparison (stdlib only).

Extends path-level validation (CONTRACTS-B2) to HTTP method granularity.
Does not import Flask, start services, or connect to a database.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RouteMethod = tuple[str, str]  # (normalized_path, METHOD)

ROUTE_DECORATOR_START_RE = re.compile(r"@\s*[\w.]+\.route\s*\(")

OPENAPI_PATH_RE = re.compile(
    r"^\s*(/[\w\-./{}<>:_]+)\s*:\s*$",
    re.MULTILINE,
)

OPENAPI_HTTP_METHOD_RE = re.compile(
    r"^\s+(get|post|put|patch|delete|head|options)\s*:\s*$",
    re.MULTILINE | re.IGNORECASE,
)

FLASK_PARAM_RE = re.compile(
    r"<(?:\w+:)?([\w_]+)>",
)

VALID_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


def normalize_flask_path(path: str) -> str:
    """Convert Flask path params to OpenAPI-style {param}."""
    normalized = FLASK_PARAM_RE.sub(r"{\1}", path)
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.rstrip("/") or "/"


def normalize_openapi_path(path: str) -> str:
    normalized = path.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.rstrip("/") or "/"


def normalize_http_method(method: str) -> str:
    upper = method.strip().upper()
    if upper not in VALID_HTTP_METHODS:
        return upper
    return upper


def param_signature(path: str) -> str:
    """Signature ignoring param names: /iot/{x}/command -> /iot/{}/command"""
    return re.sub(r"\{[^}]+\}", "{}", path)


def paths_match(a: str, b: str) -> bool:
    if a == b:
        return True
    return param_signature(a) == param_signature(b)


def extract_route_calls(text: str) -> list[RouteMethod]:
    """Parse @*.route(...) decorators and return (path, method) pairs."""
    operations: list[RouteMethod] = []
    for match in ROUTE_DECORATOR_START_RE.finditer(text):
        start = match.end()
        depth = 1
        index = start
        while index < len(text) and depth > 0:
            char = text[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            index += 1
        chunk = text[start : index - 1]

        path_match = re.search(r"['\"]([^'\"]+)['\"]", chunk)
        if not path_match:
            continue

        path = normalize_flask_path(path_match.group(1))
        methods_match = re.search(r"methods\s*=\s*\[([^\]]*)\]", chunk, re.DOTALL)
        if methods_match:
            methods = re.findall(r"['\"](\w+)['\"]", methods_match.group(1))
        else:
            methods = ["GET"]

        for method in methods:
            operations.append((path, normalize_http_method(method)))
    return operations


def scan_flask_route_methods(api_root: Path) -> set[RouteMethod]:
    operations: set[RouteMethod] = set()
    if not api_root.exists():
        raise FileNotFoundError(f"Backend API root not found: {api_root}")

    for py_file in sorted(api_root.rglob("*.py")):
        try:
            text = py_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARN: could not read {py_file}: {exc}", file=sys.stderr)
            continue
        for path, method in extract_route_calls(text):
            operations.add((path, method))
    return operations


def scan_openapi_operations(openapi_dir: Path) -> dict[str, set[RouteMethod]]:
    by_file: dict[str, set[RouteMethod]] = {}
    if not openapi_dir.exists():
        raise FileNotFoundError(f"OpenAPI dir not found: {openapi_dir}")

    for yaml_file in sorted(openapi_dir.glob("*.yaml")):
        try:
            text = yaml_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARN: could not read {yaml_file}: {exc}", file=sys.stderr)
            continue

        operations: set[RouteMethod] = set()
        path_matches = list(OPENAPI_PATH_RE.finditer(text))
        for idx, path_match in enumerate(path_matches):
            path = normalize_openapi_path(path_match.group(1))
            block_start = path_match.end()
            block_end = path_matches[idx + 1].start() if idx + 1 < len(path_matches) else len(text)
            block = text[block_start:block_end]
            for method_match in OPENAPI_HTTP_METHOD_RE.finditer(block):
                method = normalize_http_method(method_match.group(1))
                operations.add((path, method))
        by_file[yaml_file.name] = operations
    return by_file


def operation_in_set(
    path: str,
    method: str,
    candidates: set[RouteMethod],
) -> bool:
    for candidate_path, candidate_method in candidates:
        if candidate_method == method and paths_match(path, candidate_path):
            return True
    return False


def find_missing_in_openapi(
    flask_ops: set[RouteMethod],
    openapi_union: set[RouteMethod],
) -> list[RouteMethod]:
    missing: list[RouteMethod] = []
    for path, method in sorted(flask_ops, key=lambda item: (item[0], item[1])):
        if operation_in_set(path, method, openapi_union):
            continue
        missing.append((path, method))
    return missing


def find_extra_in_openapi(
    flask_ops: set[RouteMethod],
    openapi_union: set[RouteMethod],
) -> list[RouteMethod]:
    extra: list[RouteMethod] = []
    for path, method in sorted(openapi_union, key=lambda item: (item[0], item[1])):
        if operation_in_set(path, method, flask_ops):
            continue
        extra.append((path, method))
    return extra


def format_operation(path: str, method: str) -> str:
    return f"{method} {path}"


def print_report(
    flask_ops: set[RouteMethod],
    openapi_by_file: dict[str, set[RouteMethod]],
) -> None:
    openapi_union: set[RouteMethod] = set()
    for operations in openapi_by_file.values():
        openapi_union |= operations

    missing = find_missing_in_openapi(flask_ops, openapi_union)
    extra = find_extra_in_openapi(flask_ops, openapi_union)

    print("=" * 72)
    print("IBMS Flask vs OpenAPI Static Method Validation")
    print("=" * 72)
    print(f"Flask route-method pairs (static scan): {len(flask_ops)}")
    print(f"OpenAPI operations (all yaml):          {len(openapi_union)}")
    for name, operations in openapi_by_file.items():
        print(f"  - {name}: {len(operations)} operations")
    print()

    print(f"Route-methods missing in OpenAPI ({len(missing)}):")
    for path, method in missing:
        print(f"  - {format_operation(path, method)}")
    print()

    print(f"OpenAPI operations not found in Flask scan ({len(extra)}):")
    for path, method in extra:
        print(f"  - {format_operation(path, method)}")
    print()

    print("Note: contract alias paths/methods may appear as extras.")
    print("Routes without explicit methods= default to GET in Flask scan.")
    print("Param naming differences (<device_code> vs {device_did}) are normalized.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Flask @route path+method pairs with OpenAPI operations (static scan).",
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
        flask_ops = scan_flask_route_methods(backend_root)
        openapi_by_file = scan_openapi_operations(openapi_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_report(flask_ops, openapi_by_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
