# VANTARIS IBMS Security A2 JWT Secret Externalization

**Task ID:** IBMS-SECURITY-A2  
**Date:** 2026-06-16  
**Baseline Commit:** `478088f`  
**Related:** [IBMS_SECURITY_A1_SECRET_INVENTORY.md](./IBMS_SECURITY_A1_SECRET_INVENTORY.md)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Task ID | IBMS-SECURITY-A2 |
| Scope | Externalize Flask `SECRET_KEY` and JWT secret only |
| DB credentials changed | ❌ No |
| MQTT credentials changed | ❌ No |
| DID private key changed | ❌ No |
| Blockchain config changed | ❌ No |
| Modeling API auth changed | ❌ No |
| Real `.env` created | ❌ No |
| Real secret committed | ❌ No |
| Git commit | ❌ Not in this task |

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | Read `IBMS_SECRET_KEY` / `IBMS_JWT_SECRET` via `os.getenv`; dev fallbacks only |
| `AN_VANTARIS_IBMS-backend/.env.example` | Comment noting SECURITY-A2 runtime wiring |
| `docs/security/IBMS_SECURITY_A2_JWT_SECRET_EXTERNALIZATION.md` | This document |

**Not changed:** `jwt_util.py`, `main.py`, `database.py`, routes, RBAC, MQTT, DID, blockchain.

---

## 3. Environment Variables Used

| Variable | Purpose | Required In Production |
|---|---|---|
| `IBMS_SECRET_KEY` | Flask app secret key (`Config.SECRET_KEY`) | **Yes** |
| `IBMS_JWT_SECRET` | JWT signing / verification secret (`Config.JWT_SECRET_KEY`) | **Yes** |

---

## 4. Runtime Behavior

- **Environment first:** `default.py` uses `os.getenv("IBMS_SECRET_KEY")` and `os.getenv("IBMS_JWT_SECRET")` when set and non-empty.
- **Development fallback:** If unset, Flask uses `dev-only-flask-secret-do-not-use-in-production`; JWT uses the previous static dev string (`your-secret-key-change-in-production`) for local compatibility.
- **No secret printed:** Config does not log or print secret values.
- **JWT unchanged:** `jwt_util.py` still reads `JWT_SECRET_KEY` from `current_app.config` — payload format, `exp`/`iat`, algorithm (`HS256`), and `@jwt_required` behavior unchanged.
- **Route protection unchanged:** No new decorators or middleware added.

**Note:** This project does **not** load `.env` files automatically (no `python-dotenv`). Operators must export variables in the shell or use process manager env injection. Creating `.env` is out of scope for A2.

---

## 5. Not Changed

| Area | Status |
|---|---|
| Database connection | ❌ Not changed |
| MQTT credentials | ❌ Not changed |
| DID private key | ❌ Not changed |
| Blockchain config | ❌ Not changed |
| Modeling API protection | ❌ Not changed |
| RBAC policy | ❌ Not changed |
| Login / DID signature flow | ❌ Not changed |
| `requirements.txt` | ❌ Not changed |

---

## 6. Production Requirement

Production deployment **must** set:

```bash
export IBMS_SECRET_KEY='<strong-random-flask-secret>'
export IBMS_JWT_SECRET='<strong-random-jwt-secret>'
```

**Do not rely on fallback values in production.** Fallback strings are documented development defaults only.

---

## 7. Verification

| Check | Result |
|---|---|
| Grep `SECRET_KEY` / `JWT_SECRET` usage | Only `default.py` + existing `jwt_util.py` config read |
| `git diff --stat` reviewed | Single backend source file + `.env.example` + doc |
| No real `.env` created | ✅ |
| No real secret committed | ✅ Placeholders / dev fallbacks only |
| Backend source changed only in secret handling | ✅ `src/common/config/default.py` only |

Verification commands run:

```bash
grep -RIn --include="*.py" -E "SECRET_KEY|JWT_SECRET|IBMS_SECRET_KEY|IBMS_JWT_SECRET" AN_VANTARIS_IBMS-backend/src
git diff --stat
git diff -- AN_VANTARIS_IBMS-backend/src
```

Service startup and tests were **not** run per task constraints.

---

## 8. Recommended Next Tasks

| Priority | Task |
|---|---|
| 1 | **IBMS-SECURITY-A2-COMMIT** |
| 2 | **IBMS-SECURITY-A3** — Externalize DB connection string |
| 3 | **IBMS-SECURITY-A4** — Externalize MQTT credentials |
| 4 | **IBMS-CONTRACTS-A1** — OpenAPI security schemes |
| 5 | **IBMS-CORE-A0** — Unified auth middleware |

---

## 9. Related Documents

- [IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md](./IBMS_SECURITY_A0_P0_REMEDIATION_PLAN.md)
- [IBMS_SECURITY_A1_SECRET_INVENTORY.md](./IBMS_SECURITY_A1_SECRET_INVENTORY.md)
- [contracts/SECURITY_BOUNDARY.md](../../contracts/SECURITY_BOUNDARY.md)
