# Protected API Request Examples

Placeholder examples only — **no real tokens, secrets, or device credentials**.

---

## Modeling Predict

```http
POST /api/modeling/HVAC_SIM_001/predict HTTP/1.1
Host: localhost:5000
Authorization: Bearer <jwt-token-from-did-login>
X-Trace-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "timestamp": "2026-06-16T10:00:00",
  "temperature": 24.5,
  "humidity": 60
}
```

---

## IoT Device Command

```http
POST /api/iot/device/did:imbs:device:example:abc123/command HTTP/1.1
Host: localhost:5000
Authorization: Bearer <jwt-token-from-did-login>
X-Trace-Id: 550e8400-e29b-41d4-a716-446655440001
Content-Type: application/json

{
  "method": "set_temperature",
  "params": {
    "value": 24
  }
}
```

Alternative by device code:

```http
POST /api/iot/device/code/DEVICE_CODE_001/command HTTP/1.1
Authorization: Bearer <jwt-token-from-did-login>
X-Trace-Id: 550e8400-e29b-41d4-a716-446655440002
Content-Type: application/json

{
  "method": "set_temperature",
  "params": {
    "value": 24
  }
}
```

---

## IoT HTTP Ingest

```http
POST /api/iot/ingest/http HTTP/1.1
Host: localhost:5000
Authorization: Bearer <jwt-token-from-did-login>
X-Trace-Id: 550e8400-e29b-41d4-a716-446655440003
Content-Type: application/json

{
  "device_code": "DEVICE_CODE_001",
  "data": {
    "temperature": 22.1,
    "power": 1.5,
    "timestamp": "2026-06-16T10:00:00"
  }
}
```

---

## SSE Test Push

**Production:** endpoint disabled (403).

**Non-production:** requires JWT **and** `IBMS_SIMULATOR_ENABLED=true` or `IBMS_TESTMQTT_ENABLED=true`.

```http
POST /api/iot/device/HVAC_SIM_001/test-sse-push HTTP/1.1
Host: localhost:5000
Authorization: Bearer <jwt-token-from-did-login>
X-Trace-Id: 550e8400-e29b-41d4-a716-446655440004
Content-Type: application/json
```

No request body required. Response uses existing `Result.success` envelope.

---

## Obtaining a JWT (reference)

Login is **not** JWT-protected. Obtain token via challenge + signature:

```http
GET /api/did/challenge HTTP/1.1

POST /api/did/login HTTP/1.1
Content-Type: application/json

{
  "did": "did:imbs:example:entity",
  "challenge": "<challenge-from-previous-step>",
  "signature": "<signature-from-private-key>"
}
```

Response includes `token` field — use as Bearer token. **Do not commit real keys or signatures.**
