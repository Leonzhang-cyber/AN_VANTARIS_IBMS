#!/usr/bin/env python3
"""
Merge A2 permission codes into root/admin User.permission_codes (imbs_users).

DO NOT run automatically. Default is dry-run (no DB writes).

  cd AN_VANTARIS_IBMS-backend
  python scripts/assign_root_permissions.py              # dry-run
  python scripts/assign_root_permissions.py --apply      # write DB
  python scripts/assign_root_permissions.py --did did:imbs:... --apply

Does NOT run seed_permissions.py. Does NOT change passwords or login.
Users whose permissions change MUST re-login to refresh JWT perms.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, List, Sequence, Tuple

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from flask import Flask

from src.common.config.default import Config
from src.common.core.database import db, init_database
from src.DID.dao import UserDAO
from src.DID.models import User

ROOT_ASSIGNMENT_CODES: Tuple[str, ...] = (
    "modeling:read",
    "modeling:predict",
    "modeling:train",
    "iot:read",
    "iot:write",
    "iot:ingest",
    "iot:command",
    "device:read",
    "device:manage",
    "device:control",
    "did:read",
    "did:issue",
    "did:revoke",
    "did:manage",
    "system:read",
    "system:write",
    "system:admin",
    "audit:read",
)


def _build_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    init_database(app)
    return app


def _normalize_codes(codes: Iterable[str] | None) -> List[str]:
    if not codes:
        return []
    return sorted({str(c).strip() for c in codes if c and str(c).strip()})


def merge_permission_codes(existing: Iterable[str] | None, required: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Return (merged_list, newly_added_codes). Preserves existing; no removals."""
    current = _normalize_codes(existing)
    current_set = set(current)
    added = sorted(set(required) - current_set)
    merged = sorted(current_set | set(required))
    return merged, added


def resolve_target_users(session, *, did: str | None) -> List[User]:
    dao = UserDAO(session)

    if did:
        user = dao.get_by_did(did)
        if not user:
            raise SystemExit(f"[assign_root_permissions] ERROR: no user for --did {did!r}")
        return [user]

    system_users = dao.get_by_type("system")
    if not system_users:
        raise SystemExit(
            "[assign_root_permissions] ERROR: no active system-type user found. "
            "Use --did to specify the root entity."
        )

    by_username = [u for u in system_users if u.username == "system"]
    if len(by_username) == 1:
        return by_username

    if len(system_users) == 1:
        return system_users

    dids = ", ".join(u.did for u in system_users[:5])
    suffix = "..." if len(system_users) > 5 else ""
    raise SystemExit(
        f"[assign_root_permissions] ERROR: {len(system_users)} system-type users found ({dids}{suffix}). "
        "Use --did to specify exactly one target."
    )


def assign_permissions(session, users: Sequence[User], apply: bool) -> int:
    changes = 0
    for user in users:
        merged, added = merge_permission_codes(user.permission_codes, ROOT_ASSIGNMENT_CODES)
        if not added:
            print(f"[assign_root_permissions] skip {user.did} ({user.username}) — all codes present")
            continue

        changes += 1
        print(f"[assign_root_permissions] {user.did} ({user.username}) — add {len(added)} code(s): {added}")
        if apply:
            user.permission_codes = merged
            session.add(user)

    if apply and changes:
        session.commit()
        print("[assign_root_permissions] WARNING: affected users must re-login to refresh JWT perms.")
    elif not apply and changes:
        print("[assign_root_permissions] dry-run only — no DB writes. Pass --apply to persist.")

    return changes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge A2 permission codes into root/admin user(s).")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to DB (default: dry-run)",
    )
    parser.add_argument(
        "--did",
        type=str,
        default=None,
        help="Target entity DID (required when multiple system users exist)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = _build_app()
    with app.app_context():
        users = resolve_target_users(db.session, did=args.did)
        print(f"[assign_root_permissions] targets: {len(users)} user(s); apply={args.apply}")
        changes = assign_permissions(db.session, users, apply=args.apply)
        print(f"[assign_root_permissions] done — users_with_changes={changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
