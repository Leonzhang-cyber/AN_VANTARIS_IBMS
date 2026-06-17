# IBMS CONTRACTS-B4 — Method Validation Risk Review

**Task:** CONTRACTS-B4  
**Review type:** Static analysis tooling (no runtime)

---

## Static scan limitation

Method validation infers Flask operations from source text only. Routes registered programmatically, hidden behind wrappers, or generated at import time will not appear. False negatives are possible; false positives for OpenAPI-only contract aliases are expected.

---

## Method parser limitation

The `@route(...)` parser uses balanced-parenthesis extraction and regex for `methods=[...]`. Unusual decorator ordering, string concatenation for paths, or methods defined via constants may be skipped or misread.

---

## Default GET assumption risk

Flask defaults to **GET** when `methods` is omitted. If legacy code relies on implicit GET but OpenAPI documents POST (or vice versa), B4 may report misleading gaps. Always spot-check high-risk endpoints manually.

---

## No service started

Validation does not import Flask, bind ports, or execute application factory code. Results reflect static source layout only.

---

## No DB connection

No database, migration, or seed scripts are invoked.

---

## OpenAPI draft risk

OpenAPI files remain draft specifications with placeholder schemas. Method presence in YAML does not guarantee runtime behavior, auth enforcement, or response shape correctness.

---

## Recommended next validation

1. Run B4 after each OpenAPI or backend route change.
2. Pair B4 with live integration tests (CONTRACTS-A4) for critical mutations.
3. Add `x-ibms-backend-route` cross-checks when contract aliases map to different Flask paths **and** methods.
4. Document explicit `methods=` on all new Flask routes to reduce default-GET ambiguity.

---

## Sensitive route awareness

Method-level diffs highlight missing documentation for high-risk verbs (POST/PUT/DELETE) on system, DID, and IoT surfaces. Absence from OpenAPI does not mean routes are disabled — they may still be reachable at runtime without contract coverage.
