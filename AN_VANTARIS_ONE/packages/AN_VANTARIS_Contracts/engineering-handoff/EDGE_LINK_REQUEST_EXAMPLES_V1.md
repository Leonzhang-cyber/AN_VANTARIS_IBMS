# EDGE LINK Request Examples v1

## Endpoint

`https://link-gateway.example.local/edge/v1/handoff`

## Required headers

- `x-vantaris-machine-id: machine-edge-001`
- `x-vantaris-signature: FAKE_SIGNATURE_HEX_001`
- `x-vantaris-signature-algorithm: HMAC-SHA256`
- `x-vantaris-signed-at: 2026-06-17T12:00:03Z`
- `x-vantaris-trace-id: trace-demo-0001`
- `x-vantaris-idempotency-key: idem-demo-001`
- `x-vantaris-protocol-version: v1`

## Example POST /edge/v1/handoff

```bash
curl -X POST "https://link-gateway.example.local/edge/v1/handoff" \
  -H "Content-Type: application/json" \
  -H "x-vantaris-machine-id: machine-edge-001" \
  -H "x-vantaris-signature: FAKE_SIGNATURE_HEX_001" \
  -H "x-vantaris-signature-algorithm: HMAC-SHA256" \
  -H "x-vantaris-signed-at: 2026-06-17T12:00:03Z" \
  -H "x-vantaris-trace-id: trace-demo-0001" \
  -H "x-vantaris-idempotency-key: idem-demo-001" \
  -H "x-vantaris-protocol-version: v1" \
  --data-binary @AN_VANTARIS_Contracts/dto-examples/signed-handoff-envelope.example.json
```

## Expected accepted ack

```json
{
  "schemaVersion": "v1",
  "protocolVersion": "v1",
  "messageId": "00000000-0000-4000-8000-000000000111",
  "ackId": "00000000-0000-4000-8000-000000000222",
  "correlationId": "00000000-0000-4000-8000-000000000333",
  "ackAt": "2026-06-17T12:00:00Z",
  "status": "accepted"
}
```

## Expected retryable failure ack

```json
{
  "schemaVersion": "v1",
  "protocolVersion": "v1",
  "messageId": "00000000-0000-4000-8000-000000005001",
  "correlationId": "00000000-0000-4000-8000-000000005004",
  "ackAt": "2026-06-17T12:00:22Z",
  "status": "rejected",
  "retryable": true,
  "retryAfterSeconds": 30,
  "rejectionReasons": [
    "delivery_retry"
  ]
}
```

## Expected signature error

```json
{
  "schemaVersion": "v1",
  "code": "INVALID_SIGNATURE",
  "message": "signature verification failed",
  "correlationId": "00000000-0000-4000-8000-000000000333"
}
```

## Expected version mismatch error

```json
{
  "schemaVersion": "v1",
  "code": "UNSUPPORTED_VERSION",
  "message": "unsupported protocolVersion for edge handoff",
  "correlationId": "00000000-0000-4000-8000-000000000333"
}
```
