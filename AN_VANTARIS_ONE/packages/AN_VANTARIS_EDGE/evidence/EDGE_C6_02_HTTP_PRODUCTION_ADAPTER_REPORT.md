# EDGE C6-02 HTTP Production Adapter Report

## Scope

`UFMS-EDGE-C6-02` introduces the first real-connectivity production adapter for the `http` connector: a controlled, read-only, GET/HEAD HTTP/HTTPS client isolated from runtime registration.

## Baseline

- `4716d31 feat(edge): add file production readonly adapter`

## Modified files

- `src/connectors/http/production/http-production-adapter.types.ts`
- `src/connectors/http/production/http-production-target-policy.ts`
- `src/connectors/http/production/http-production-response-normalizer.ts`
- `src/connectors/http/production/http-production-readonly-adapter.ts`
- `src/connectors/http/production/index.ts`
- `deploy/offline-bundle/scripts/verify-http-production-readonly-adapter-edge.sh`
- `scripts/validation/edge-c6-http-production-adapter-dry-run.sh`
- `scripts/validation/edge-c6-http-production-adapter-smoke.sh`
- `scripts/validation/lib/http-production-adapter-dry-run-cases.cjs`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_02_HTTP_PRODUCTION_ADAPTER_REPORT.md`

## Adapter architecture

Production code lives under `src/connectors/http/production/` and is isolated from foundation modules under `src/connectors/http/`.

Call chain:

1. HTTP production configuration validation
2. Target reference resolution (`targetReferenceId` → controlled base URL via provider)
3. URL policy validation (scheme, userinfo, fragment, relative path, allowlist)
4. DNS resolution with all-result IP revalidation
5. Credential/header reference resolution (reference IDs only in tracked config)
6. Read-only GET/HEAD request via Node built-in `node:http` / `node:https`
7. Redirect hop revalidation (when enabled)
8. Bounded response/header read and content-type enforcement
9. JSON / NDJSON / CSV parsing with Foundation integration
10. Canonical normalized result returned to explicit caller only

Public interface exposes `readOnce()` and `headOnce()` only. Not registered in runtime index, connector-manager, or connector-registry.

## GET/HEAD only

- Allowed methods: `GET`, `HEAD`
- Rejected: `POST`, `PUT`, `PATCH`, `DELETE`, `CONNECT`, `TRACE`, `OPTIONS`, unknown methods
- No write/send/post/put/patch/delete/upload/mutate APIs exported

## SSRF and target policy

- Tracked config stores `targetReferenceId` + `relativePath` only — no arbitrary absolute URLs, secrets, or inline credentials
- Schemes: production requires HTTPS; validation test mode allows HTTP only for explicit loopback fixtures (`tlsMode: LOOPBACK_HTTP_TEST`)
- Rejects userinfo, fragments, protocol-relative URLs, backslash confusion, empty hostname, non-allowlisted targets
- Uses existing foundation `validateHttpDestination` / `evaluateSsrfRisk` via production-built policy
- Opaque error references: `http-target:<targetReferenceId>:<sha256-16>`, host hash via `createHostReferenceHash()`

## Metadata rejection

Explicit deny list includes:

- `169.254.169.254`, `100.100.100.200`
- `metadata.google.internal`, `metadata.azure.internal`
- `localhost`, `localhost.localdomain`

Also rejects link-local, loopback, private ranges, IPv4-mapped IPv6 bypass, and DNS resolution to forbidden IPs (fail closed on mixed safe/unsafe results).

## DNS policy

- Production: `dnsMode: VALIDATED_RESOLVER` with `node:dns/promises` lookup; all A/AAAA results validated before connect
- Validation test mode: `dnsMode: INJECTED_TEST` with deterministic injected resolver (no external DNS)
- DNS result count capped; errors use reference IDs only

## Redirect policy

- Default `maxRedirects=0` (fail closed)
- When enabled: strict hop limit, statuses 301/302/303/307/308 only
- Each hop revalidates scheme, host, port, DNS, resolved IP
- HTTPS→HTTP downgrade rejected; redirect loops rejected; sensitive headers not carried cross-origin

## TLS policy

- `rejectUnauthorized: true`, minimum TLS 1.2, SNI enabled
- Rejects `NODE_TLS_REJECT_UNAUTHORIZED=0` at runtime
- No inline PEM, no certificate values in tracked config or logs
- Test self-signed paths use HTTP loopback in validation mode — TLS verification is not disabled

## Credential and header security

- Tracked config stores reference IDs only (`credentialReferenceId`, `headerReferenceIds`, `certificateReferenceId`)
- In-memory reference providers used in validation harness only
- Header allowlist enforcement; rejects Host override, hop-by-hop headers, CRLF injection, duplicate Authorization
- Secrets never logged or returned in errors

## Response limits

Enforced with hard caps:

- `maxResponseBytes`, `maxHeaderBytes`, `maxHeaderCount`
- `connectTimeoutMs`, `responseTimeoutMs`, `maxProcessingMilliseconds`
- `maxJsonDepth`, `maxRecordCount`, `maxFieldCount`, `maxFieldLength`
- `maxRedirects`, `maxDnsResults`

Invalid config (non-integer, NaN, Infinity, string numbers, over-cap) fails closed with `HTTP_CONFIG_INVALID`.

## Supported formats

- `application/json`
- `application/x-ndjson` (per-line Foundation validation via `validateFoundationJsonRecord` → `parseHttpJsonResponse`)
- `text/csv` (via `parseHttpCsvResponse`)

Rejects: `text/html`, `application/octet-stream`, gzip/deflate (compression bomb risk), unknown/missing content-type unless explicitly allowed.

## Parser security

- `JSON.parse` only — no eval/Function
- Dangerous keys (`__proto__`, `prototype`, `constructor`) rejected at any depth
- Formula prefix protection (`=`, `+`, `-`, `@`)
- NDJSON: accurate `lineNumber`, no partial success on failure
- CSV: quoted fields, escaped quotes; multiline quoted fields unsupported (fail closed)

## Foundation integration

Production adapter calls existing HTTP foundation modules:

- `validateHttpPollingPolicy`
- `validateHttpDestination` / `evaluateSsrfRisk`
- `validateHttpResponseMetadata`
- `parseHttpJsonResponse` / `parseHttpCsvResponse`

Foundation files were not modified. No LINK/DB direct access.

## Error redaction

Errors use stable codes only. They do not include full URLs, query values, credentials, headers, response bodies, resolved sensitive IPs, or certificate content.

## Local fixture server (validation)

- Binds `127.0.0.1` on ephemeral port only (never `0.0.0.0`)
- Unique `.runtime/validation-sessions/c6-02/` sandbox
- Server closed after tests; no public network; no external DNS in harness

## Verifier

`deploy/offline-bundle/scripts/verify-http-production-readonly-adapter-edge.sh` verifies:

- Production directory and required files
- GET/HEAD only; no write methods or third-party HTTP clients
- SSRF/metadata/DNS/redirect/TLS/header/response-limit controls
- Foundation integration; runtime isolation; package drift vs HEAD
- Connector matrix and freeze gates unchanged

Negative matrix: **30/30 rejected, 0 leaked**

## Validation results

| Check | Result |
|-------|--------|
| `npm run typecheck:edge` | PASS |
| `edge-c6-http-production-adapter-dry-run.sh` | PASS (189/189) |
| `edge-c6-http-production-adapter-smoke.sh` | PASS |
| `verify-http-production-readonly-adapter-edge.sh` | PASS |
| `validate-edge-package.sh` | PASS |
| `edge-boundary-scan.sh` | PASS |
| `validate-ufms-ibms-isolation.sh` | PASS (`hard_fail_count=0`) |

## Gate state (unchanged)

- `readOnlyFoundationEnforcementGate=PASS`
- `controlledPilotGate=DEFERRED`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `realConnectivityEnabled=false`
- `supportsWriteback=false`
- `productionDependencyIncluded=false`

## Runtime and dependency posture

- No runtime registration
- No package.json / package-lock.json changes vs HEAD
- No npm install / no new dependencies
- Node built-in modules only: `node:http`, `node:https`, `node:dns/promises`, `node:crypto`, `node:url`

## Remaining limitations

- HTTP Production Adapter Code Complete ≠ Pilot Approval
- HTTP Production Adapter Code Complete ≠ Production Approval
- `realConnectivityEnabled` remains `false`
- No writeback, no polling scheduler, no keep-alive connection pool
- Verifier uses static heuristics supplemented by adapter/verifier negative fixtures
- Production HTTPS credential/certificate providers deferred to deployment phase

## Readiness keys

- `UFMS_EDGE_C6_02_HTTP_PRODUCTION_ADAPTER_PASS`
- `HTTP_PRODUCTION_READONLY_ADAPTER_VERIFIED`
- `HTTP_GET_HEAD_ONLY`
- `HTTP_TARGET_ALLOWLIST_ENFORCED`
- `HTTP_SSRF_GUARD_ENFORCED`
- `HTTP_METADATA_TARGETS_REJECTED`
- `HTTP_DNS_RESULTS_REVALIDATED`
- `HTTP_REDIRECT_HOPS_REVALIDATED`
- `HTTP_TLS_VALIDATION_REQUIRED`
- `HTTP_CREDENTIAL_REFERENCES_ONLY`
- `HTTP_RESPONSE_LIMITS_ENFORCED`
- `HTTP_JSON_NDJSON_CSV_SUPPORTED`
- `HTTP_DANGEROUS_KEYS_REJECTED`
- `HTTP_FORMULA_PREFIX_PROTECTED`
- `HTTP_FOUNDATION_VALIDATION_INTEGRATED`
- `HTTP_ERROR_REDACTION_VERIFIED`
- `NO_HTTP_WRITE_METHOD`
- `NO_RUNTIME_REGISTRATION`
- `CONNECTOR_STILL_BLOCKED`
