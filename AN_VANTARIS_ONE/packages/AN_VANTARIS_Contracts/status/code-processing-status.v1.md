# Code Processing Status (v1)

Lifecycle states inside AN_VANTARIS_Code after LINK delivery accept (data flow steps 7–12).

## Pipeline steps

| Step | Name | Status when active |
|------|------|--------------------|
| 7 | Core receive | `received` |
| 8 | Core dedupe | `dedupe_check` |
| 9 | Rule matching | `rule_matching` |
| 10 | NexusAI orchestration | `nexus_orchestration` |
| 11 | Work order creation | `work_order_creation` |
| 12 | Notification intent and audit | `notification_audit` |

## Terminal statuses

| Status | Description |
|--------|-------------|
| `completed` | All applicable steps succeeded |
| `skipped_nexus` | Rule path bypassed NexusAI |
| `failed_validation` | Failed before persistence |
| `failed_nexus` | NexusAI call failed (retryable) |
| `failed_persistence` | DB write failed |
| `failed_notification` | Audit/notification intent failed |

## Correlation

All statuses MUST carry `correlationId` from the original LINK envelope.

## References

- Schema: `schemas/nexus-triage-request.v1.schema.json`
- Schema: `schemas/nexus-triage-response.v1.schema.json`
- OpenAPI: `openapi/code-to-nexusai.v1.yaml`
