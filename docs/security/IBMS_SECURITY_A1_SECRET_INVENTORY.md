# VANTARIS IBMS Security A1 Secret Inventory

**Task ID:** IBMS-SECURITY-A1  
**Date:** 2026-06-16  
**Baseline Commit:** `387274d`  
**Related:** [IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md](./IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Task ID | IBMS-SECURITY-A1 |
| Scope | Create `.env.example` and secret inventory only |
| Runtime code changed | ❌ No |
| Secret moved | ❌ No |
| Real secret committed | ❌ No |
| Service started | ❌ No |
| Dependency installed | ❌ No |
| Git commit | ❌ Not in this task |

---

## 2. Files Created

| File | Purpose |
|---|---|
| `AN_VANTARIS_IBMS-backend/.env.example` | Placeholder environment variable template |
| `docs/security/IBMS_SECURITY_A1_SECRET_INVENTORY.md` | This document — secret category inventory |

---

## 3. Environment Variable Baseline

| Variable | Purpose | Placeholder Only | Runtime Wired |
|---|---|---|---|
| `IBMS_ENV` | Environment name (`development` / `staging` / `production`) | Yes | No / pending SECURITY-A2+ |
| `IBMS_DEBUG` | Debug mode flag | Yes | No / pending SECURITY-A2+ |
| `IBMS_SECRET_KEY` | Flask application secret | Yes | No / pending SECURITY-A2+ |
| `IBMS_JWT_SECRET` | JWT signing secret | Yes | No / pending SECURITY-A2+ |
| `IBMS_DATABASE_URL` | Full SQLAlchemy database URI | Yes | No / pending SECURITY-A3+ |
| `IBMS_DB_HOST` | MySQL host | Yes | No / pending SECURITY-A3+ |
| `IBMS_DB_PORT` | MySQL port | Yes | No / pending SECURITY-A3+ |
| `IBMS_DB_NAME` | Database name | Yes | No / pending SECURITY-A3+ |
| `IBMS_DB_USER` | Database user | Yes | No / pending SECURITY-A3+ |
| `IBMS_DB_PASSWORD` | Database password | Yes | No / pending SECURITY-A3+ |
| `IBMS_MQTT_HOST` | MQTT broker host | Yes | No / pending SECURITY-A4+ |
| `IBMS_MQTT_PORT` | MQTT broker port | Yes | No / pending SECURITY-A4+ |
| `IBMS_MQTT_USERNAME` | MQTT username | Yes | No / pending SECURITY-A4+ |
| `IBMS_MQTT_PASSWORD` | MQTT password | Yes | No / pending SECURITY-A4+ |
| `IBMS_DID_PRIVATE_KEY` | System DID private key | Yes | No / pending SECURITY-A5+ |
| `IBMS_BLOCKCHAIN_RPC_URL` | Blockchain RPC endpoint | Yes | No / pending SECURITY-A5+ |
| `IBMS_BLOCKCHAIN_CHAIN_ID` | Blockchain chain ID | Yes | No / pending SECURITY-A5+ |
| `IBMS_BLOCKCHAIN_CONTRACT_ADDRESS` | Anchor contract address | Yes | No / pending SECURITY-A5+ |
| `IBMS_SIMULATOR_ENABLED` | Enable Edge simulators | Yes | No / pending SECURITY-A8+ |
| `IBMS_MODELING_API_ENABLED` | Enable modeling API routes | Yes | No / pending SECURITY-A6+ |
| `IBMS_TESTMQTT_ENABLED` | Enable testMQTT tooling | Yes | No / pending SECURITY-A8+ |
| `IBMS_UPLOAD_DIR` | Upload directory path | Yes | No / pending future Storage task |
| `IBMS_MAX_UPLOAD_MB` | Max upload size (MB) | Yes | No / pending future Storage task |
| `IBMS_TRACE_ENABLED` | Distributed trace logging | Yes | No / pending SECURITY-A9+ |
| `IBMS_AUDIT_ENABLED` | Audit log recording | Yes | No / pending SECURITY-A9+ |

> **Note:** All variables are documented in `.env.example` only. Backend runtime still reads hardcoded values from `src/common/config/default.py` and related modules until SECURITY-A2 through A5 wire env loading.

---

## 4. Known Secret Categories from B2

Values are **not listed** — categories and remediation tasks only.

| Secret Category | Current Risk | Future Task |
|---|---|---|
| DB credential | Hardcoded in `default.py` / `database.py` | SECURITY-A3 |
| JWT secret | Hardcoded static default in config | SECURITY-A2 |
| Flask secret key | Not env-controlled today | SECURITY-A2 |
| DID private key | Hardcoded in config; startup print risk in `main.py` | SECURITY-A5 |
| MQTT credential | Hardcoded in config and `testMQTT` simulators | SECURITY-A4 |
| Blockchain RPC / contract | Hardcoded node URLs and contract address in `blockchain/config.py` | SECURITY-A5 |
| Test credential JSON | Sample files under `src/tests/` | Review in SECURITY-A7 / separate hygiene task |

---

## 5. No Real Secret Confirmation

| Check | Result |
|---|---|
| `.env.example` contains placeholders only | ✅ |
| No real password is included | ✅ |
| No real private key is included | ✅ |
| No real token is included | ✅ |
| No real production host credential is included | ✅ |
| Existing runtime code still uses current config | ✅ Until SECURITY-A2+ |

Placeholder patterns used: `replace-with-*`, `127.0.0.1`, `ibms_user`, `ibms_db`, `9527` (documented public chain ID from config structure, not a secret).

---

## 6. Future Wiring Plan

| Task | Action |
|---|---|
| **SECURITY-A2** | Wire Flask secret + JWT secret to `IBMS_SECRET_KEY` / `IBMS_JWT_SECRET` |
| **SECURITY-A3** | Wire DB connection to `IBMS_DATABASE_URL` or component vars |
| **SECURITY-A4** | Wire MQTT credentials to `IBMS_MQTT_*` in drivers and simulators |
| **SECURITY-A5** | Wire DID private key + blockchain RPC/contract to env; stop private key printing |
| **SECURITY-A6** | Protect modeling API; optionally gate with `IBMS_MODELING_API_ENABLED` |
| **SECURITY-A7** | Protect device command and ingest APIs |
| **SECURITY-A8** | Disable simulator routes when `IBMS_SIMULATOR_ENABLED=false` / production |
| **SECURITY-A9** | Wire audit/trace flags; require `traceId` on sensitive boundaries |

---

## 7. Verification Checklist

| Check | Result |
|---|---|
| `git diff --stat` reviewed | ✅ Backend `src/` not in diff |
| `.env.example` reviewed for real secrets | ✅ Placeholders only |
| `.gitignore` still excludes `.env` and `.env.*` | ✅ Root `.gitignore` lines 6–8; `!.env.example` allows example file |
| `backend/src` not modified | ✅ |
| No runtime behavior changed | ✅ |

---

## 8. No-Code-Change Confirmation

| Check | Result |
|---|---|
| No backend source code was modified | ✅ |
| No frontend source code was modified | ✅ |
| No real `.env` file was created | ✅ |
| No runtime config was changed | ✅ |
| No dependency was installed | ✅ |
| No service was started | ✅ |

---

## 9. Related Documents

- [IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md](./IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md)
- [contracts/SECURITY_BOUNDARY.md](../../contracts/SECURITY_BOUNDARY.md)
- [IBMS_BACKEND_INVENTORY_B2.md](../architecture/IBMS_BACKEND_INVENTORY_B2.md)

---

## 10. Recommended Next Task

**IBMS-SECURITY-A2** — Externalize JWT and Flask secrets to environment variables (first runtime wiring step).
