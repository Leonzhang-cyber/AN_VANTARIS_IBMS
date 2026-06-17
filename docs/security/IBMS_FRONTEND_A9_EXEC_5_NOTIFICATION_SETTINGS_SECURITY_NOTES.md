# IBMS FRONTEND-A9-EXEC-5 — Notification Settings Security Notes

**Task:** FRONTEND-A9-EXEC-5  
**Risk level:** Medium (channel configuration surface)

---

## Notification settings may expose sensitive channel endpoints

Real notification configuration can include webhook URLs, SMTP hosts, SMS provider credentials, and Teams/Slack incoming webhook paths. This migration shows **placeholder rows only** with no endpoint values.

---

## No webhook secret/token shown

The page must not display webhook secrets, bearer tokens, SMTP passwords, or API keys. Current implementation shows channel names and generic descriptions only.

---

## Backend must enforce system:admin or system:write later

When notification APIs are implemented, create/update/test operations should require `system:admin` or `system:write` on the server. Test-notification endpoints must be rate-limited and audited.

---

## Frontend route permission is not security

Route meta `permissions: ['system:read']` is advisory. It does not authorize API access or protect channel secrets stored on the server.

---

## No direct axios

`NotificationSettingsView.vue` performs no HTTP requests.

---

## No production URL hardcode

No external webhook or SMTP URLs embedded in source.

---

## Local placeholder must be clearly labeled

Channel table tags, alert banner, and empty state state **Local placeholder / API pending** so operators cannot mistake UI samples for live configuration.

---

## Disabled Save/Test

Save and Test buttons remain disabled until a vetted backend API exists. Do not enable without server-side validation and authorization.
