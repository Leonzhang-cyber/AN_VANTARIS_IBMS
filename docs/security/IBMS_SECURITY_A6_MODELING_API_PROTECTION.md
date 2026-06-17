# VANTARIS IBMS Security A6 Modeling API Protection

## 1. Task Scope

- Task ID: IBMS-SECURITY-A6
- Scope: protect `/api/modeling/*` with JWT/RBAC boundary
- No DB schema changed
- No model algorithm changed
- No CSV / pkl artifact changed
- No login logic changed
- No global RBAC refactor
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/data_modeling/modeling_api.py` | Added `@jwt_required` to all modeling routes |
| `docs/security/IBMS_SECURITY_A6_MODELING_API_PROTECTION.md` | This document |

## 3. Protected Routes

| Route | Method | Protection Applied | Notes |
|---|---|---|---|
| `/api/modeling/csv/list` | GET | `@jwt_required` | CSV file listing |
| `/api/modeling/csv/<device_code>` | GET | `@jwt_required` | Device CSV info |
| `/api/modeling/<device_code>/train` | POST | `@jwt_required` | Model training |
| `/api/modeling/<device_code>/predict` | POST | `@jwt_required` | Single-point prediction |
| `/api/modeling/<device_code>/predict_future` | POST | `@jwt_required` | Multi-day forecast |
| `/api/modeling/<device_code>/model_info` | GET | `@jwt_required` | Model metadata |
| `/api/modeling/<device_code>/<method>` | GET, POST | `@jwt_required` | Generic predictor dispatch |

All routes require `Authorization: Bearer <token>` using the existing JWT utility.

## 4. Auth Strategy

- Existing `@jwt_required` decorator from `src.common.utils.jwt_util` reused (same pattern as `system_api.py` and `did_api.py`).
- JWT payload format not changed (`sub`, `perms`, optional `frontend_perms` / `api_perms`).
- Login behavior not changed.
- Fine-grained permission enforcement (`modeling:read`, `modeling:train`, etc.) is **not** applied in this task; `verify_api_permission()` exists but is not wired globally. RBAC refinement pending **IBMS-CORE-A0** / **IBMS-SECURITY-A6B**.

## 5. Recommended Permissions

Target permission codes for future CORE-A0 / SECURITY-A6B (not seeded in this task):

| Permission | Suggested use |
|---|---|
| `modeling:read` | CSV list, CSV info, model_info |
| `modeling:predict` | predict, predict_future |
| `modeling:train` | train |

These are documentation targets only; no DB seed or permission table migration in A6.

## 6. Not Changed

- DB config not changed.
- MQTT not changed.
- DID / blockchain not changed.
- Simulator not changed.
- Model training logic not changed.
- Predictor logic not changed.
- CSV / pkl files not changed.
- Login / JWT payload not changed.

## 7. Verification

- `modeling_api.py` reviewed: 7 routes, 7 `@jwt_required` decorators.
- All `/api/modeling/*` routes now require JWT; no exceptions.
- `git diff` reviewed; changes limited to decorator import and route guards.
- No real secret committed.
- No service started.

## 8. Recommended Next Tasks

- IBMS-SECURITY-A6-COMMIT
- IBMS-SECURITY-A6B — fine-grained modeling permissions if needed
- IBMS-SECURITY-A7 — device command API protection
- IBMS-SECURITY-A8 — disable simulator in production
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
