# IBMS FRONTEND-A9-EXEC-6 — Integration Settings Security Notes

**Task:** FRONTEND-A9-EXEC-6  
**Risk level:** High (integration credentials surface)

---

## Integration settings may expose secrets/API keys

Production integration UIs often store MQTT credentials, webhook signing secrets, OAuth client secrets, and cross-system API keys. This migration intentionally shows **no secrets** — only integration type labels and placeholder status.

---

## No API key/secret/token shown

No API keys, bearer tokens, private keys, or connection strings appear in source, table data, or documentation examples.

---

## Backend must enforce system:admin or system:write later

Integration create/update/test must require elevated system permissions on the server. Secrets should be stored server-side (vault/KMS), never returned in full to the client after initial setup.

---

## Frontend route permission is not security

Route meta `permissions: ['system:read']` is advisory. It does not prevent direct API access or protect stored connector credentials.

---

## No direct axios

`IntegrationSettingsView.vue` performs no HTTP requests.

---

## No production URL hardcode

No MQTT broker, webhook, or external IBMS URLs hardcoded in the page.

---

## Local placeholder must be clearly labeled

Integration rows, alert banner, and empty state indicate **Local placeholder / API pending**.

---

## Disabled Save/Test

Prevents implied connectivity tests against undefined endpoints. Enable only with authenticated, authorized backend integration APIs.
