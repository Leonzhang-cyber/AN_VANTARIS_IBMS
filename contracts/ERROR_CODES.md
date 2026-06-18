# VANTARIS ONE Error Codes

| Code | Category | Meaning | Owner Domain |
| --- | --- | --- | --- |
| `CONTRACT_SCHEMA_INVALID` | contracts | Contract payload/schema validation failed. | contracts |
| `CONTRACT_VERSION_UNSUPPORTED` | contracts | Contract version is not supported by consumer. | contracts |
| `CONTRACT_REQUIRED_FIELD_MISSING` | contracts | Required contract field is absent. | contracts |
| `AUTH_MACHINE_IDENTITY_REQUIRED` | auth | Machine identity is required for this operation. | trust |
| `AUTH_SIGNATURE_INVALID` | auth | Signature check failed for authenticated request. | trust |
| `AUTH_TOKEN_INVALID` | auth | Auth token is invalid or expired for contract operation. | trust |
| `SECURITY_PAYLOAD_HASH_MISMATCH` | security | Payload hash verification failed. | security |
| `SECURITY_REPLAY_DETECTED` | security | Replay attack detected by idempotency/replay controls. | security |
| `DELIVERY_TARGET_UNAVAILABLE` | delivery | Delivery target endpoint is unavailable. | edge-link |
| `DELIVERY_RETRY_EXHAUSTED` | delivery | Delivery retries exhausted without success. | edge-link |
| `DELIVERY_DUPLICATE_MESSAGE` | delivery | Duplicate message detected during delivery pipeline. | edge-link |
| `DELIVERY_ROUTE_NOT_FOUND` | delivery | No routing policy matches the delivery target. | integration |
| `DLQ_MESSAGE_CREATED` | delivery | Message moved to dead-letter queue. | edge-link |
| `EDGE_CONNECTOR_NOT_FOUND` | edge | Referenced edge connector is not found. | edge-link |
| `EDGE_PROTOCOL_UNSUPPORTED` | edge | Requested edge protocol is unsupported. | edge-link |
| `EDGE_TAG_UNMAPPED` | edge | Vendor tag cannot map to canonical point identity. | edge-link |
| `LINK_ACK_TIMEOUT` | link | ACK not received within policy timeout window. | edge-link |
| `MODULE_LICENSE_DISABLED` | module | Module capability disabled by license policy. | ibms-core |
| `PATCH_SIGNATURE_INVALID` | patch | Patch signature validation failed. | trust |
| `DB_MIGRATION_REQUIRED` | db | Required migration level not satisfied for contract change. | db |
| `CDE_EVIDENCE_REQUIRED` | cde | Required CDE evidence is missing. | cde |
| `AI_GUARDRAIL_BLOCKED` | ai | AI request blocked by configured guardrail policy. | ai |
| `UFMS_ADAPTER_CONTRACT_INVALID` | adapter | UFMS adapter contract payload is invalid. | integration |
