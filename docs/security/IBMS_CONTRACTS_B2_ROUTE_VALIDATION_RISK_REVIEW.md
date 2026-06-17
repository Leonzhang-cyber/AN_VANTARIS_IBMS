# IBMS Contracts B2 Route Validation Risk Review

## 1. Static scan limitation

- Tool does not execute Flask or validate runtime blueprint registration
- False negatives possible if routes use non-standard decorators

## 2. No service started

- No network, no auth, no secret exposure
- Safe for CI documentation checks

## 3. No DB connection

- Script reads files only

## 4. Path param mismatch risk

- Normalizer maps `<device_code>` ↔ `{device_code}` and `{device_did}` via signature matching
- Different param names on same segment may false-positive as missing

## 5. OpenAPI draft risk

- 39 backend routes not in current OpenAPI union — expected gap
- Draft specs must not be treated as complete security boundary

## 6. Recommended next validation

- Add HTTP method comparison
- Split report by OpenAPI file (protected vs frontend)
- Lock baseline file after CONTRACTS-B3 expansion
- Optional: integrate with `PERMISSION_MATRIX_A2.md` per route

## 7. Non-scope

- No backend/frontend runtime modified
- No yaml route content changed in B2
