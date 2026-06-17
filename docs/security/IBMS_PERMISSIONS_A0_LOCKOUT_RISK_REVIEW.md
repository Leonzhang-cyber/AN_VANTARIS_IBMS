# IBMS Permissions A0 Lockout Risk Review

**Task:** IBMS-PERMISSIONS-A0  
**Type:** Security prep — inventory only

---

## Empty Permission Risk

| Scenario | HTTP | Impact |
|---|---|---|
| Valid JWT, `perms: []` or absent | 403 on A6B/A7B/A10B routes | Integrators with JWT-only access lose all fine-grained APIs |
| New entity with no `permission_codes` in DB | Login embeds empty `perms` | Same lockout after first login |
| Test/staging users never seeded | 403 across enforced routes | Blocks QA until seed aligned |

**Mitigation before seed:** Document required codes per role; ensure root/system entity receives full table or `*` at login.

---

## Stale JWT Permission Risk

Permissions are snapshotted into JWT at `/api/did/login`. Changes via:

- `User.permission_codes` update in DB
- `/api/system/permissions` CRUD
- VC reissue with new permissions

…do **not** affect outstanding tokens until expiry or re-login.

**Impact:** Revoked permissions may still work until JWT expires (default 8h from config).

**Future options:** Shorter TTL, permission version claim, forced re-login, live DB check (separate task).

---

## Admin / Root Wildcard Risk

- Helper allows `*` and `domain:*` in JWT `perms`.
- Root entity gets all `perm_code` values from `imbs_permission` — if table is empty/incomplete, root may also lock out.
- Storing literal `*` in DB for root simplifies bootstrap but grants unrestricted access through helper.

**Recommendation:** Seed complete code list first; optionally add `*` only for bootstrap system DID.

---

## Machine Identity Risk

No separate login path for:

- HTTP ingest service accounts
- Edge device identities
- MQTT/simulator automation

These would need JWT from a DID with `iot:ingest` / `device:control` — not yet standardized.

---

## Rollback Strategy

1. **Revert A6B/A7B/A10B commits** — routes fall back to JWT-only (401 without token, 200/4xx with any valid JWT).
2. **Revert CORE-A1** — remove permission decorators import; keep JWT guards.
3. **Seed rollback** — separate DB task; does not require code revert if codes are additive.

---

## Verification Plan Before DB Seed Change

| Step | Action |
|---|---|
| V1 | Export current `imbs_permission` rows and root `User.permission_codes` |
| V2 | Map each enforced route to required code (A2 matrix) |
| V3 | Identify DIDs/users that login today with empty `perms` |
| V4 | Staging login test: confirm JWT payload includes expected `perms` after seed |
| V5 | Spot-check 401 (no token) vs 403 (token, missing code) vs 200 (token, code present) |
| V6 | Document re-login requirement for permission changes |

---

## Related Documents

- `docs/architecture/IBMS_PERMISSIONS_A0_RUNTIME_INVENTORY.md`
- `docs/security/IBMS_SECURITY_A6B_MODELING_PERMISSION_ENFORCEMENT.md`
- `docs/security/IBMS_SECURITY_A7B_IOT_PERMISSION_ENFORCEMENT.md`
- `docs/security/IBMS_SECURITY_A10B_DID_PERMISSION_ENFORCEMENT.md`
