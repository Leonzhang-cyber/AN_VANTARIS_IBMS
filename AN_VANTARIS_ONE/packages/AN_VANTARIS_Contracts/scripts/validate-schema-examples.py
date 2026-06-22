#!/usr/bin/env python3
"""Lightweight semantic validation of contract examples against mapped schemas.

Scope intentionally shallow and deterministic:
- JSON parse for schemas/examples
- top-level object type check where schema type is object
- required top-level fields exist and are non-null in examples
- secret marker scan in example files
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


SECRET_RE = re.compile(
    r"BEGIN PRIVATE KEY|AWS_SECRET|PASSWORD=|SECRET=|TOKEN=|private_key|client_secret",
    re.IGNORECASE,
)


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / "VANTARIS_UFMS_PACKAGE_COORDINATION.md").is_file():
            return current
        current = current.parent
    raise RuntimeError("validate-schema-examples: cannot locate repo root")


def mapped_pairs() -> Dict[str, List[Tuple[str, str]]]:
    return {
        "P0": [
            ("AN_VANTARIS_Contracts/dto-examples/wire-event.example.json", "AN_VANTARIS_Contracts/schemas/wire-event-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/machine-identity-ref.example.json", "AN_VANTARIS_Contracts/schemas/machine-identity-ref-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/signature-headers.example.json", "AN_VANTARIS_Contracts/schemas/signature-headers-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/signed-handoff-envelope.example.json", "AN_VANTARIS_Contracts/schemas/signed-handoff-envelope-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/edge-handoff-event.example.json", "AN_VANTARIS_Contracts/schemas/edge-handoff-event-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/delivery-ack-partial-success.example.json", "AN_VANTARIS_Contracts/schemas/delivery-ack.v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/delivery-ack-retryable-failure.example.json", "AN_VANTARIS_Contracts/schemas/delivery-ack.v1.schema.json"),
        ],
        "Canonical": [
            ("AN_VANTARIS_Contracts/dto-examples/canonical/tenant.example.json", "AN_VANTARIS_Contracts/schemas/tenant-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/site.example.json", "AN_VANTARIS_Contracts/schemas/site-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/building.example.json", "AN_VANTARIS_Contracts/schemas/building-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/floor.example.json", "AN_VANTARIS_Contracts/schemas/floor-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/space.example.json", "AN_VANTARIS_Contracts/schemas/space-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/gateway.example.json", "AN_VANTARIS_Contracts/schemas/gateway-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/connector.example.json", "AN_VANTARIS_Contracts/schemas/connector-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/source-system.example.json", "AN_VANTARIS_Contracts/schemas/source-system-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/asset.example.json", "AN_VANTARIS_Contracts/schemas/asset-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/device.example.json", "AN_VANTARIS_Contracts/schemas/device-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/point.example.json", "AN_VANTARIS_Contracts/schemas/point-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/telemetry.example.json", "AN_VANTARIS_Contracts/schemas/telemetry-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/event.example.json", "AN_VANTARIS_Contracts/schemas/event-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/alarm.example.json", "AN_VANTARIS_Contracts/schemas/alarm-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/evidence.example.json", "AN_VANTARIS_Contracts/schemas/evidence-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/health.example.json", "AN_VANTARIS_Contracts/schemas/health-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/throughput.example.json", "AN_VANTARIS_Contracts/schemas/throughput-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/sync-batch.example.json", "AN_VANTARIS_Contracts/schemas/sync-batch-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/audit.example.json", "AN_VANTARIS_Contracts/schemas/audit-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/canonical/config-version.example.json", "AN_VANTARIS_Contracts/schemas/config-version-v1.schema.json"),
        ],
        "Reliability": [
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-delivery-attempt.example.json", "AN_VANTARIS_Contracts/schemas/link-delivery-attempt-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-retry-policy.example.json", "AN_VANTARIS_Contracts/schemas/link-retry-policy-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-dlq-item.example.json", "AN_VANTARIS_Contracts/schemas/link-dlq-item-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-replay-request.example.json", "AN_VANTARIS_Contracts/schemas/link-replay-request-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-replay-result.example.json", "AN_VANTARIS_Contracts/schemas/link-replay-result-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-delivery-batch.example.json", "AN_VANTARIS_Contracts/schemas/link-delivery-batch-v1.schema.json"),
            ("AN_VANTARIS_Contracts/dto-examples/reliability/link-partition-state.example.json", "AN_VANTARIS_Contracts/schemas/link-partition-state-v1.schema.json"),
        ],
    }


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = find_repo_root(Path(__file__).parent)
    groups = mapped_pairs()

    failures: List[str] = []
    checked_pairs = 0
    parsed_schema_count = 0
    parsed_example_count = 0

    # Parse all schemas/examples to satisfy baseline parse coverage.
    for path in sorted((root / "AN_VANTARIS_Contracts" / "schemas").glob("*.json")):
        try:
            read_json(path)
            parsed_schema_count += 1
        except Exception as exc:
            failures.append(f"JSON parse FAIL schema {path}: {exc}")

    for path in sorted((root / "AN_VANTARIS_Contracts" / "dto-examples").rglob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
            read_json(path)
            parsed_example_count += 1
            if SECRET_RE.search(text):
                failures.append(f"Secret marker FAIL example {path}")
        except Exception as exc:
            failures.append(f"JSON parse FAIL example {path}: {exc}")

    # Semantic checks on explicit mapping.
    for _, pairs in groups.items():
        for ex_rel, schema_rel in pairs:
            checked_pairs += 1
            ex_path = root / ex_rel
            schema_path = root / schema_rel

            if not ex_path.is_file():
                failures.append(f"Missing mapped example: {ex_rel}")
                continue
            if not schema_path.is_file():
                failures.append(f"Missing mapped schema: {schema_rel}")
                continue

            try:
                schema_obj = read_json(schema_path)
                ex_obj = read_json(ex_path)
            except Exception:
                # Already surfaced in parse stage.
                continue

            schema_type = schema_obj.get("type")
            if schema_type == "object" and not isinstance(ex_obj, dict):
                failures.append(f"Type FAIL {ex_rel}: expected top-level object")
                continue

            required = schema_obj.get("required", [])
            if isinstance(required, list):
                for field in required:
                    if field not in ex_obj:
                        failures.append(f"Required field missing {ex_rel}: {field}")
                    elif ex_obj[field] is None:
                        failures.append(f"Required field null {ex_rel}: {field}")

    if failures:
        print("validate-schema-examples: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("validate-schema-examples: PASS")
    print(f"- parsed schemas: {parsed_schema_count}")
    print(f"- parsed examples: {parsed_example_count}")
    print(f"- checked mapped pairs: {checked_pairs}")
    print(f"- groups: {', '.join(groups.keys())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
