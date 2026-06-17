# VANTARIS IBMS Security A5 DID Blockchain Externalization

**Task ID:** IBMS-SECURITY-A5  
**Date:** 2026-06-16  
**Baseline Commit:** `e87c9dd` (A4)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Scope | Externalize DID private key and blockchain config only |
| Stop private key printing | ✅ Yes |
| DID business behavior changed | ❌ No |
| Contract redeployed | ❌ No |
| Real private key committed | ❌ No (dev fallback only) |
| Service started | ❌ No |

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | `system_did_private_key` from `IBMS_DID_PRIVATE_KEY` |
| `AN_VANTARIS_IBMS-backend/src/blockchain/config.py` | `NODE_URLS`, `CHAIN_ID`, `ANCHOR_CONTRACT_ADDRESS` from env |
| `AN_VANTARIS_IBMS-backend/src/main.py` | Removed private key value from startup logs |
| `AN_VANTARIS_IBMS-backend/.env.example` | SECURITY-A5 comment |
| `docs/security/IBMS_SECURITY_A5_DID_BLOCKCHAIN_EXTERNALIZATION.md` | This document |

**Unchanged:** `IMBSAnchor.sol`, ABI array, DID/VC/VP service logic, contract deploy scripts.

---

## 3. Environment Variables Used

| Variable | Purpose |
|---|---|
| `IBMS_DID_PRIVATE_KEY` | DID signing private key (`Config.system_did_private_key`) |
| `IBMS_BLOCKCHAIN_RPC_URL` | Blockchain RPC endpoint(s); comma-separated for multi-node |
| `IBMS_BLOCKCHAIN_CHAIN_ID` | Chain ID |
| `IBMS_BLOCKCHAIN_CONTRACT_ADDRESS` | Anchor contract address |

---

## 4. Runtime Behavior

- **Environment first** for all four variables when set and non-empty.
- **Development fallback** when unset:
  - DID private key: pre-existing dev constant in `_DEV_DID_PRIVATE_KEY`
  - RPC URLs: three-node dev list in `_DEV_NODE_URLS`
  - Chain ID: `9527`
  - Contract address: existing dev anchor address
- **`IBMS_BLOCKCHAIN_RPC_URL`:** Single URL or comma-separated list (replaces entire `NODE_URLS`).

---

## 5. Private Key Logging Rule

| Rule | Implementation |
|---|---|
| No private key value in logs | ✅ Removed `print(f"私钥: {result.get('private_key')}")` |
| Allowed status only | ✅ Prints `DID private key configured: yes/no` |
| User guidance | Message directs operator to save key via secure channel (not stdout) |

---

## 6. Not Changed

| Area | Status |
|---|---|
| DB | ❌ Not changed |
| MQTT | ❌ Not changed |
| JWT | ❌ Not changed |
| Modeling API | ❌ Not changed |
| RBAC | ❌ Not changed |
| DID/VC/VP payload & issuance logic | ❌ Not changed |
| Contract ABI / Solidity | ❌ Not changed |
| Contract redeploy | ❌ Not performed |

---

## 7. No Real Secret Confirmation

- No new real DID private key added to committed source beyond existing dev fallback constant.
- `.env.example` uses `replace-with-did-private-key` placeholder only.
- Startup no longer emits private key material.

---

## 8. Production Requirement

Production **must** set:

- `IBMS_DID_PRIVATE_KEY`
- `IBMS_BLOCKCHAIN_RPC_URL` (or accept single-node URL)
- `IBMS_BLOCKCHAIN_CHAIN_ID`
- `IBMS_BLOCKCHAIN_CONTRACT_ADDRESS`

Do not rely on development fallbacks in production.

---

## 9. Recommended Next Tasks

- **IBMS-SECURITY-A5-COMMIT** (included in batch)
- **IBMS-SECURITY-A6** — Protect modeling API
- **IBMS-SECURITY-A7** — Protect device command APIs
- **IBMS-SECURITY-A8** — Disable simulators in production
- **IBMS-SECURITY-A9** — Audit traceId
