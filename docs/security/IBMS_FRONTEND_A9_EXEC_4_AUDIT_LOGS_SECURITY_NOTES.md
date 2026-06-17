# IBMS FRONTEND-A9-EXEC-4 — Audit Logs Security Notes

**Task:** FRONTEND-A9-EXEC-4  
**Risk level:** Medium (audit visibility surface)

---

## Audit logs may contain sensitive operational traces

Real audit feeds can include actor DIDs, permission changes, device commands, and IP/trace metadata. This migration shows **placeholder rows only** until a vetted backend API exists.

Production audit UIs must redact secrets and limit fields to authorized viewers.

---

## Do not expose secrets/tokens

Placeholder content must not include JWTs, private keys, passwords, or production credentials. Current page uses generic placeholder text only.

---

## Backend must enforce audit:read

When audit APIs are implemented, the server must require `audit:read` (or stricter) on query endpoints. Write/export of audit trails should be separately permissioned and audited.

---

## Frontend route permission is not security

Route meta `permissions: ['audit:read']` is advisory for future guards. It does not block API access or guarantee authorization.

---

## No direct axios

`AuditLogsView.vue` performs no HTTP requests.

---

## No production URL hardcode

No external API URLs embedded in the page.

---

## Local placeholder must be clearly labeled

Table rows, tags, alerts, and empty state explicitly state **Local placeholder / API pending** so operators cannot mistake sample UI for live audit data.

---

## Filter disabled state

Search and filters are disabled to prevent implied functionality until backend contract exists. Re-enable only with authenticated, authorized API integration.
