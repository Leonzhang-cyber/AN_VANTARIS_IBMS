# IBMS FRONTEND-A9-EXEC-3 — System Overview Security Notes

**Task:** FRONTEND-A9-EXEC-3  
**Risk level:** Low (navigation only)

---

## Overview page is navigation only

This page displays module cards and routes users to other System views. It does not load or mutate server configuration. Sensitive data exposure risk is limited to module titles and permission label text.

---

## Frontend route permission is not security

Route meta `permissions: ['system:read']` is advisory for future client guards. It does not enforce backend authorization. Users can still attempt direct navigation or API calls regardless of card visibility.

---

## Backend remains source of truth

Required permission labels on cards (`system:read`, `system:admin`) are UX hints for operators. Actual access control for audit logs, notifications, and integrations must be enforced on the server when those APIs and pages are implemented.

---

## No direct axios

The overview view performs no HTTP requests. Navigation uses Vue Router only.

---

## No raw secret copied

No tokens, passwords, private keys, or production credentials appear in source or documentation.

---

## No production URL hardcode

Card paths are application-relative routes (`/system/permissions`, etc.). No external API URLs are embedded.

---

## Pending cards must not imply permission enforcement

Cards marked **Pending migration** have disabled actions. Their permission labels describe intended future policy — not current runtime enforcement. Do not treat pending modules as protected until backend routes and guards exist.
