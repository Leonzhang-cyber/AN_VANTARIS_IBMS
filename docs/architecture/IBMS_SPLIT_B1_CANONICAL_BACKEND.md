# VANTARIS IBMS Split B1 Canonical Backend Declaration

## 1. Task Scope

- declare canonical backend package only
- no source moved
- no backend runtime changed
- no raw source modified or deleted
- no service started
- no dependency installed
- no migration/seed executed

Prerequisites: SOURCE-A1, SPLIT-A0, WORKSPACE-A1 (`5571524`).

---

## 2. Canonical Decision

| Role | Package path | Status |
|---|---|---|
| **Canonical runtime backend** | `AN_VANTARIS_IBMS-backend/` | **LOCKED** — sole executable backend for IBMS split |
| **Raw reference backend** | `AN_VANTARIS_IBMS-ibms_backend/` | read-only inventory input; **gitignored** |
| **Not canonical** | `AN_VANTARIS_IBMS-ibms_backend/` as runtime replacement | **FORBIDDEN** |

**Entrypoint:** `AN_VANTARIS_IBMS-backend/src/main.py`  
**API prefix:** `/api` via `src/api/` blueprints (system, menu, did, iot, sse, modeling)  
**Security line:** JWT + permission enforcement through commit `56234d8` and A6–A10 series.

---

## 3. Why Not Raw `ibms_backend`

| Factor | Raw `ibms_backend` | Canonical `AN_VANTARIS_IBMS-backend` |
|---|---|---|
| Config | Hardcoded DB/JWT/MQTT/DID secrets in `default.py` | Env-first `IBMS_*` vars + `.env.example` |
| menu_api | 19 routes **without** JWT | All routes `@jwt_required` |
| modeling_api | Unprotected | JWT + `modeling:*` permissions |
| iot_api | Write paths unprotected | JWT + `device:*` / `iot:*` permissions |
| did_api | Partial JWT | JWT + `did:manage/issue/revoke` |
| permission_util | Missing | Present |
| Seed scripts | Only under `src/scripts/` | Root `scripts/seed_permissions.py`, `assign_root_permissions.py` |
| Simulator guards | Unguarded test endpoints | `_runtime_guard.py`, A8 guards |

**Diff summary (read-only `diff -rq` on `src/`):** ~25 file differences; current backend is a **security-evolved superset** of the same module tree. No unique production feature identified in raw that requires replacing canonical.

---

## 4. Raw Source Handling (B1.2)

Already enforced by WORKSPACE-A1:

- `.gitignore` ignores `AN_VANTARIS_IBMS-ibms_backend/`
- Raw package remains on disk for read-only diff/inventory
- Wholesale commit or copy from raw → canonical is **prohibited**

See: `docs/architecture/IBMS_WORKSPACE_A1_RAW_SOURCE_GUARD.md`

---

## 5. Environment Template Check (B1.4)

`.env.example` at `AN_VANTARIS_IBMS-backend/.env.example` documents:

| Category | Variables |
|---|---|
| App / JWT | `IBMS_ENV`, `IBMS_DEBUG`, `IBMS_SECRET_KEY`, `IBMS_JWT_SECRET` |
| Database | `IBMS_DATABASE_URL`, `IBMS_DB_*` |
| MQTT | `IBMS_MQTT_*` |
| DID / Blockchain | `IBMS_DID_PRIVATE_KEY`, `IBMS_BLOCKCHAIN_*` |
| Test fixtures | `IBMS_TEST_DID_PRIVATE_KEY` (placeholder) |
| Feature flags | `IBMS_SIMULATOR_ENABLED`, `IBMS_MODELING_API_ENABLED`, `IBMS_TESTMQTT_ENABLED` |
| Storage / audit | `IBMS_UPLOAD_DIR`, `IBMS_MAX_UPLOAD_MB`, `IBMS_TRACE_ENABLED`, `IBMS_AUDIT_ENABLED` |

**Verdict:** Env template covers all `IBMS_*` keys referenced in `src/common/config/default.py`. No new env keys required for B1 declaration.

---

## 6. Migration Rules (Future B4)

When porting logic from raw reference:

1. Never copy `ibms_backend/src/common/config/default.py` literals
2. Never remove `@jwt_required` or `@require_permission` from canonical routes
3. Port feature deltas only after diff review and contract update
4. Simulator/testMQTT changes must preserve A8 production guards
5. Artifacts (`data/*.pkl`, test CSV/mp4) stay outside runtime package

---

## 7. Exit Criteria (B1)

| Criterion | Met |
|---|---|
| No ambiguity about runtime backend | Yes — `AN_VANTARIS_IBMS-backend` |
| Raw backend marked reference-only | Yes — gitignore + WORKSPACE-A1 |
| No secret in tracked canonical config | Yes — env-first placeholders |
| Backend runtime unchanged | Yes — docs only |

---

## 8. Next Tasks

- **IBMS-SPLIT-B2** — Declare canonical frontend source package
- **IBMS-SPLIT-B3** — Create frontend target skeleton
- **CONTRACTS-B1** — Frontend-facing OpenAPI subset
