# IBMS Source A1 Backend Risk Review

Scope: read-only comparison of `AN_VANTARIS_IBMS-ibms_backend` vs `AN_VANTARIS_IBMS-backend`.  
No values reproduced below.

---

## 1. Secret risk

| Risk | Location | Severity | Mitigation |
|---|---|---|---|
| Hardcoded DB password and host | `ibms_backend/src/common/config/default.py` | **Critical** | Never import this file into canonical backend; current backend uses `IBMS_DATABASE_URL` / component env vars |
| Hardcoded JWT secret | same | **Critical** | Current backend: `IBMS_JWT_SECRET` externalization (A2) |
| Hardcoded DID private key | same | **Critical** | Current backend: `IBMS_DID_PRIVATE_KEY` (A5) |
| Hardcoded MQTT broker host | same | **High** | Current backend: `IBMS_MQTT_*` (A4) |
| IDE dataSources.xml | `ibms_backend/.idea/` | Medium | Exclude from Git and split packages |

---

## 2. Duplicated config risk

- Two backend trees with **identical module names** but **divergent config and auth** create confusion if both are treated as runnable.
- `requirements.txt` parity suggests dependency drift is low; **behavior drift is high** (security decorators).
- **Rule:** Only `AN_VANTARIS_IBMS-backend` is executable canonical; `ibms_backend` is archive.

---

## 3. Migration risk

| Risk | Description |
|---|---|
| Accidental rollback | Copying files from `ibms_backend` over current backend would **remove** JWT on menu/modeling/IoT and permission checks |
| Secret propagation | Blind copy of `default.py` reintroduces P0 secrets |
| Artifact pollution | `data/*.pkl`, `testMQTT/*.mp4` may land in production image |
| __pycache__ | Should be stripped on any future copy |
| Duplicate scripts | `src/scripts/` vs root `scripts/` — merge policy needed in B4 |

---

## 4. DB connection risk

- Original uses inline `mysql+pymysql://user:password@host:port/db` with remote-looking host.
- Current backend builds URI from env with safe dev fallbacks.
- **Import order:** establish env contract → validate connectivity in staging → never run migration against prod from original package.

---

## 5. Auth compatibility risk

| Surface | Original | Current | Frontend impact |
|---|---|---|---|
| menu_api | Open | JWT required | Frontend must send Bearer on all menu calls (already does via `request.js`) |
| modeling_api | Open | JWT + permissions | UI pages calling modeling need token + role seeds |
| iot_api write paths | Open | JWT + permissions | Device admin flows need permission assignment |
| did_api mutate | Mostly open | JWT + permissions | DID admin flows need aligned roles |
| Public read routes | Some IoT/DID reads open | Unchanged on many GETs | Verify contract doc per route |

---

## 6. Frontend compatibility risk

- Frontend (`ibms_front`) only has `system_api.js` and `did_api.js` — many views are UI shells without dedicated API modules.
- Backend permission enforcement may cause **403** on routes frontend previously accessed without auth — seed alignment required before integration test.
- Menu JWT protection (56234d8) aligns with frontend token interceptor — **compatible** if token present.

---

## 7. Recommended safe import order

When phase B migration begins (not this batch):

1. **contracts/** — OpenAPI + permission matrix for each route group  
2. **docs/security/** — Confirm no secret in diff  
3. **AN_VANTARIS_IBMS-backend** config layer (env only)  
4. **Core/Auth/System** — already in current backend  
5. **menu_api** — keep JWT guards  
6. **Modeling / IoT / DID** — port logic only from original if missing features; **never** downgrade guards  
7. **Simulator/testMQTT** — last; production guard flags  
8. **data/models artifacts** — external storage only  
9. **Frontend** — after backend contract validation  

**Stop conditions during import:**

- Real secret detected in diff → halt  
- Route loses JWT vs current backend → reject merge  
- Unknown duplicate module → inventory before copy
