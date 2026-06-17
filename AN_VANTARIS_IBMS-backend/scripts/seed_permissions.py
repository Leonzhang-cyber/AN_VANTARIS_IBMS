#!/usr/bin/env python3
"""
Idempotent seed for imbs_permission rows (A2 / A6B / A7B / A10B codes).

DO NOT run automatically at app startup. Default is dry-run (no DB writes).

  cd AN_VANTARIS_IBMS-backend
  python scripts/seed_permissions.py              # dry-run
  python scripts/seed_permissions.py --apply      # write DB

(Sys.path is adjusted automatically; requires IBMS_DB_* or IBMS_DATABASE_URL in environment.)

Does NOT assign permissions to users. Does NOT delete existing rows.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Backend root = parent of scripts/
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

try:
    from flask import Flask

    from src.common.config.default import Config
    from src.common.core.database import db, init_database
    from src.system.dao import PermissionDAO
    from src.system.models import Permission
except ImportError as exc:
    print(f"[seed_permissions] ERROR: import failed — {exc}")
    raise SystemExit(1) from exc

# perm_code -> description (human-readable; safe to update on re-run)
PERMISSION_SEED: Dict[str, str] = {
    "modeling:read": "Read modeling CSV, model info, and read-side predictor calls",
    "modeling:predict": "Run modeling predict and predict_future",
    "modeling:train": "Train modeling pipelines",
    "iot:read": "Read IoT device and dictionary data",
    "iot:write": "Create or update IoT standard fields and methods",
    "iot:ingest": "HTTP telemetry ingest",
    "iot:command": "Dispatch IoT device commands",
    "device:read": "Read device details and mappings",
    "device:manage": "Register, update, delete devices and mappings",
    "device:control": "Device control commands and reconnect",
    "did:read": "Read DID entity and session info",
    "did:issue": "Issue VC, reissue, and generate VP",
    "did:revoke": "Revoke verifiable credentials",
    "did:manage": "Create entities and manage DID hierarchy",
    "system:read": "Read system configuration and menus",
    "system:write": "Write system standard fields, methods, and menus",
    "system:admin": "Administer permissions and system structure",
    "audit:read": "Read audit and trace records",
}


@dataclass
class SeedPlan:
    create: List[str] = field(default_factory=list)
    update: List[str] = field(default_factory=list)
    skip: List[str] = field(default_factory=list)


def _build_app() -> Flask:
    """Minimal Flask app with DB only — avoids create_app blockchain/IoT startup."""
    app = Flask(__name__)
    app.config.from_object(Config)
    init_database(app)
    return app


def plan_seed(session) -> SeedPlan:
    """Inspect DB and build planned create/update/skip lists without writing."""
    plan = SeedPlan()
    for perm_code, description in PERMISSION_SEED.items():
        existing: Permission | None = PermissionDAO.get_by_code(session, perm_code)
        if existing:
            if existing.description != description:
                plan.update.append(perm_code)
            else:
                plan.skip.append(perm_code)
            continue
        plan.create.append(perm_code)
    return plan


def apply_seed(session, plan: SeedPlan) -> Tuple[int, int, int]:
    """Apply planned changes and commit. Never deletes. Never assigns users."""
    created = updated = skipped = 0

    for perm_code in plan.create:
        PermissionDAO.create(
            session,
            perm_code=perm_code,
            description=PERMISSION_SEED[perm_code],
        )
        created += 1

    for perm_code in plan.update:
        existing = PermissionDAO.get_by_code(session, perm_code)
        if existing:
            PermissionDAO.update(session, existing, description=PERMISSION_SEED[perm_code])
            updated += 1

    skipped = len(plan.skip)
    session.commit()
    return created, updated, skipped


def _print_plan(plan: SeedPlan) -> None:
    print(f"[seed_permissions] planned create ({len(plan.create)}): {plan.create or '—'}")
    print(f"[seed_permissions] planned update ({len(plan.update)}): {plan.update or '—'}")
    print(f"[seed_permissions] planned skip ({len(plan.skip)}): {plan.skip or '—'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed imbs_permission rows (idempotent).")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to DB (default: dry-run)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.apply:
        print("[seed_permissions] APPLY MODE: database changes enabled")
    else:
        print("[seed_permissions] DRY RUN: no database changes")

    try:
        app = _build_app()
    except Exception as exc:
        print(f"[seed_permissions] ERROR: bootstrap failed — {exc}")
        return 1

    with app.app_context():
        try:
            plan = plan_seed(db.session)
        except Exception as exc:
            print(f"[seed_permissions] ERROR: database read failed — {exc}")
            return 1

        _print_plan(plan)
        total = len(PERMISSION_SEED)

        if not args.apply:
            print(
                f"[seed_permissions] dry-run summary — "
                f"would_create={len(plan.create)}, would_update={len(plan.update)}, "
                f"would_skip={len(plan.skip)}, expected={total}"
            )
            print("[seed_permissions] Pass --apply to persist changes.")
            return 0

        try:
            created, updated, skipped = apply_seed(db.session, plan)
        except Exception as exc:
            db.session.rollback()
            print(f"[seed_permissions] ERROR: apply failed — {exc}")
            return 1

        print(
            f"[seed_permissions] done — created={created}, updated={updated}, "
            f"skipped={skipped}, expected={total}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
