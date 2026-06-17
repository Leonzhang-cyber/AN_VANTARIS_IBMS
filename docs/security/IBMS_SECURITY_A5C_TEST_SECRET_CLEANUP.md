# VANTARIS IBMS Security A5C Test Secret Cleanup

## 1. Task Scope

- Task ID: IBMS-SECURITY-A5C
- Scope: remove hardcoded private keys from test files only
- Runtime code not changed
- DID/VC/VP business logic not changed
- Blockchain runtime not changed
- No real .env created
- No real private key committed
- No test executed
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/tests/did_signature.py` | Removed hardcoded and commented private keys; reads `IBMS_TEST_DID_PRIVATE_KEY`; skips when unset; does not print key value |
| `AN_VANTARIS_IBMS-backend/src/tests/vc_test.py` | Removed hardcoded private key from fixture; reads `IBMS_TEST_DID_PRIVATE_KEY` or writes placeholder |
| `AN_VANTARIS_IBMS-backend/.env.example` | Added `IBMS_TEST_DID_PRIVATE_KEY` placeholder for manual test scripts |
| `docs/security/IBMS_SECURITY_A5C_TEST_SECRET_CLEANUP.md` | This document |

## 3. Cleanup Summary

| File | Issue | Action |
|---|---|---|
| `src/tests/did_signature.py` | hardcoded test private key | replaced with `IBMS_TEST_DID_PRIVATE_KEY` env; exit with safe message when unset |
| `src/tests/vc_test.py` | hardcoded test private key | replaced with env or `replace-with-test-did-private-key` placeholder |

## 4. Test Key Policy

- Test private keys must not be committed.
- Test private keys must be provided through `IBMS_TEST_DID_PRIVATE_KEY` if needed.
- `.env` remains gitignored.
- `.env.example` may contain placeholder only.
- Test scripts must not print private key values.

## 5. Not Changed

- Runtime DID code not changed.
- Blockchain runtime not changed.
- Contract config not changed.
- DB / MQTT / JWT not changed.
- Modeling API not changed.
- RBAC not changed.

## 6. Verification

- `git grep` reviewed for hardcoded private key patterns in target test files.
- No real private key committed.
- No real `.env` created.
- Changes limited to test secret cleanup.

## 7. Recommended Next Tasks

- IBMS-SECURITY-A5C-COMMIT
- IBMS-SECURITY-A6
- IBMS-SECURITY-A7
- IBMS-SECURITY-A8
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
