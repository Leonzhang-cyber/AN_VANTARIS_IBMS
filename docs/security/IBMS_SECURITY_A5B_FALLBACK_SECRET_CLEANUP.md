# VANTARIS IBMS Security A5B Fallback Secret Cleanup

## 1. Task Scope

- Task ID: IBMS-SECURITY-A5B
- Scope: remove real or historical secrets from development fallbacks
- Env-first behavior remains
- No business behavior intentionally changed
- No real .env created
- No real secret committed
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | Replaced DB, DID, JWT, MQTT dev fallbacks with non-sensitive placeholders |
| `AN_VANTARIS_IBMS-backend/src/blockchain/config.py` | Replaced remote RPC URLs and production contract address with local/empty fallbacks |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/hvac_mqtt_simulator.py` | MQTT credential fallbacks aligned to placeholders |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/air_quality_simulator.py` | MQTT credential fallbacks aligned to placeholders |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/test_air_quality_receiver.py` | MQTT credential fallbacks aligned to placeholders |
| `AN_VANTARIS_IBMS-backend/.env.example` | Added SECURITY-A5B note on placeholder-only fallbacks |
| `docs/security/IBMS_SECURITY_A5B_FALLBACK_SECRET_CLEANUP.md` | This document |

## 3. Cleanup Categories

| Category | Action | Real Secret Removed |
|---|---|---|
| DB fallback password | replaced with placeholder | Yes |
| DB fallback host/port | replaced with local defaults (`127.0.0.1:3306`) | Yes |
| JWT fallback | verified dev-only placeholder | Yes |
| Flask secret fallback | verified dev-only placeholder | Yes |
| MQTT fallback | replaced with local placeholder | Yes |
| DID private key fallback | removed (empty string when env unset) | Yes |
| Blockchain RPC fallback | changed to local placeholder (`127.0.0.1`) | Yes |
| Contract address fallback | replaced with empty string | Yes |

## 4. Runtime Compatibility Notes

- Production must set env variables (`IBMS_*`); do not rely on dev fallbacks.
- Local development may need shell export or a gitignored `.env` copied from `.env.example`.
- `.env` is gitignored; `.env.example` contains placeholders only.
- DID signing and blockchain anchoring require explicit env config when fallbacks are empty or point to local placeholders.
- `IBMS_BLOCKCHAIN_CHAIN_ID=9527` remains the documented local dev chain id default when unset.

## 5. Not Changed

- DB schema not changed.
- MQTT topics/payloads not changed.
- DID/VC/VP business logic not changed.
- Blockchain contract not changed.
- Modeling API auth not changed.
- RBAC not changed.
- Route protection not changed.

## 6. Verification

- `git grep` reviewed for secret-like fallback patterns in allowed source paths.
- No real `.env` created.
- No real secret committed.
- `.env.example` contains placeholders only.
- Backend source changes limited to fallback cleanup in config and testMQTT simulators.

## 7. Recommended Next Tasks

- IBMS-SECURITY-A5B-COMMIT
- IBMS-SECURITY-A6
- IBMS-SECURITY-A7
- IBMS-SECURITY-A8
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
