# IBMS Security A6B Modeling Permission Enforcement

**Task ID:** IBMS-SECURITY-A6B  
**Date:** 2026-06-16

---

## 1. Task Scope

- Enforce fine-grained permissions on modeling API routes
- Reuse CORE-A1 `permission_util` decorators after existing `@jwt_required`
- No model algorithm, CSV/pkl, request/response, login, or JWT payload changes

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/data_modeling/modeling_api.py` | Added `@require_permission` / `@require_any_permission` |
| `docs/security/IBMS_SECURITY_A6B_MODELING_PERMISSION_ENFORCEMENT.md` | This document |

---

## 3. Route Permission Matrix

| Route | Method | Handler | Permission |
|---|---|---|---|
| `/api/modeling/csv/list` | GET | `list_csv_files` | `modeling:read` |
| `/api/modeling/csv/<device_code>` | GET | `get_device_csv_info` | `modeling:read` |
| `/api/modeling/<device_code>/train` | POST | `train` | `modeling:train` |
| `/api/modeling/<device_code>/predict` | POST | `predict` | `modeling:predict` |
| `/api/modeling/<device_code>/predict_future` | POST | `predict_future` | `modeling:predict` |
| `/api/modeling/<device_code>/model_info` | GET | `get_model_info` | `modeling:read` |
| `/api/modeling/<device_code>/<method>` | GET, POST | `call_method` | `modeling:read` **or** `modeling:predict` |

**Note on `call_method`:** Generic predictor dispatch may invoke read-only or predict-like methods; `require_any_permission(['modeling:read', 'modeling:predict'])` allows either role until per-method classification is added.

---

## 4. Not Changed

- Handler bodies and response envelopes
- Training / prediction service logic
- CSV and pkl storage
- JWT login and token payload
- DB schema / seed

---

## 5. Empty Permission / Stale Permission Risk

- Valid JWT with empty `perms` → **403** on all modeling routes
- Permissions are JWT snapshot from login; DB updates require re-login to take effect

---

## 6. Recommended Next Tasks

- IBMS-SECURITY-A7B — IoT write/command/ingest permissions
- IBMS-SECURITY-A10B — DID high-risk permissions
- DB seed alignment for `modeling:*` codes on operator/engineer roles
- Optional per-method classification for `call_method` route
