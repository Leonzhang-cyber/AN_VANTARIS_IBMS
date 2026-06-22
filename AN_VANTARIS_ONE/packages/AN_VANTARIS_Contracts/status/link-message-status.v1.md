# Link Message Status (v1)

Lifecycle states for messages flowing from AN_VANTARIS_LINK to AN_VANTARIS_Code.

## States

| Status | Owner | Description |
|--------|-------|-------------|
| `queued` | LINK | Message accepted into LINK outbound queue |
| `delivering` | LINK | Delivery attempt in progress toward Code |
| `delivered` | LINK | HTTP 202 received from Code |
| `delivery_failed` | LINK | Transport or Code rejection before accept |
| `accepted` | Code | Code accepted envelope for processing |
| `duplicate` | Code | Dedupe detected; no reprocessing |
| `rejected` | Code | Schema or policy rejection |
| `processing` | Code | Core pipeline active (steps 7–12) |
| `completed` | Code | Processing finished successfully |
| `failed` | Code | Processing error after accept |

## Transitions

```
queued → delivering → delivered → accepted → processing → completed
                    ↘ delivery_failed
delivered → duplicate
delivered → rejected
accepted → processing → failed
```

## Ack mapping

`delivery-ack.v1` `status` values map to terminal LINK-side states:

- `accepted` → `delivered` then Code `accepted`
- `duplicate` → `duplicate`
- `rejected` → `rejected`

## References

- Schema: `schemas/link-message-envelope.v1.schema.json`
- Schema: `schemas/delivery-ack.v1.schema.json`
- OpenAPI: `openapi/link-to-code-delivery.v1.yaml`
