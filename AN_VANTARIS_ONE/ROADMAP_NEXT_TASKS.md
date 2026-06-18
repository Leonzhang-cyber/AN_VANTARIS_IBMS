# VANTARIS ONE Next Task Roadmap

## Immediate Next Recommended Task

CONTRACTS-A0-MANIFEST-BASELINE

Reason:

Contracts coverage is PARTIAL. Before Edge/Link/Code runtime migration, Contracts must define manifest, versioning, object identity, API namespace policy, Edge normalized object, Link envelope/ACK/retry/DLQ, module manifest, patch manifest, license VC, CDE base schema.

## Parallel Optional Task

EDGE-SOURCE-AUDIT

Reason:

AN_VANTARIS_EDGE runtime package does not exist. Current protocol drivers remain inside AN_VANTARIS_IBMS-backend/src/Iot/drivers. Need source audit before extraction.

## Not Yet Allowed

- REBRAND runtime rename
- backend move
- frontend move
- DB rename
- API namespace change
- production package split

## Recommended Sequence

1. CONTRACTS-A0-MANIFEST-BASELINE
2. EDGE-SOURCE-AUDIT
3. CONTRACTS-A1-EDGE-LINK-SCHEMAS
4. EDGE-A0-SKELETON-PACKAGE
5. DB-SCHEMA-BASELINE
6. CODE-MODULE-A0
7. CONSOLE-MODULE-A0
