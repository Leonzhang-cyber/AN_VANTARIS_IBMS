"""Deterministic digest helpers for registry artifacts."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_digest(payload: Any) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
