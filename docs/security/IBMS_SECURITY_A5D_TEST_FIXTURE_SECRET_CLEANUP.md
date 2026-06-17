# VANTARIS IBMS Security A5D Test Fixture Secret Cleanup

## 1. Task Scope

- Task ID: IBMS-SECURITY-A5D
- Scope: remove private keys from tracked JSON test fixtures only
- Runtime code not changed
- Test scripts not changed
- DID/VC/VP business logic not changed
- No real .env created
- No real private key committed
- No test executed
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/tests/credential_cb7664f1.json` | Replaced `private_key` with placeholder |
| `AN_VANTARIS_IBMS-backend/src/tests/credential_1d53138a.json` | Replaced `private_key` with placeholder |
| `AN_VANTARIS_IBMS-backend/src/tests/vc_credential.json` | Replaced `private_key` with placeholder |
| `docs/security/IBMS_SECURITY_A5D_TEST_FIXTURE_SECRET_CLEANUP.md` | This document |

**Reviewed, unchanged:** `vp_test.json`, `vc_test.json` — no `private_key` field present.

## 3. Cleanup Summary

| File | Issue | Action |
|---|---|---|
| `credential_cb7664f1.json` | hardcoded test private key | replaced with `replace-with-test-did-private-key` |
| `credential_1d53138a.json` | hardcoded test private key | replaced with `replace-with-test-did-private-key` |
| `vc_credential.json` | hardcoded test private key | replaced with `replace-with-test-did-private-key` |

## 4. Fixture Policy

- JSON fixtures must not contain real private keys.
- JSON fixtures may contain placeholders only.
- Test-only placeholders must be clearly invalid.
- No private key value may be printed or committed.

## 5. Not Changed

- Runtime DID code not changed.
- Blockchain runtime not changed.
- DB / MQTT / JWT not changed.
- Modeling API not changed.
- RBAC not changed.

## 6. Verification

- `git grep` reviewed for private key patterns in `src/tests/*.json`.
- No real private key committed.
- No real `.env` created.
- Changes limited to JSON fixture cleanup.

## 7. Recommended Next Tasks

- IBMS-SECURITY-A5D-COMMIT
- IBMS-SECURITY-A6
- IBMS-SECURITY-A7
- IBMS-SECURITY-A8
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
