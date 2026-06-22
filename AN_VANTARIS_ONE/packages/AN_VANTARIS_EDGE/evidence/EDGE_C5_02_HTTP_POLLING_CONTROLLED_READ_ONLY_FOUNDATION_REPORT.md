# EDGE C5-02 HTTP Polling Controlled Read-only Foundation Report

## Scope

`UFMS-EDGE-C5-02` introduces local controlled read-only HTTP polling foundation for the `http` connector only.

## Baseline

- `d758e84 feat(edge): add file import readonly foundation`

## HTTP connector current maturity

- `currentMaturity=FOUNDATION_READY`
- `requestedMode=FOUNDATION_ONLY`
- `permittedMode=SYNTHETIC_ONLY`
- `syntheticFixtureOnly=true`
- `realConnectivityEnabled=false`
- `productionDependencyIncluded=false`
- `supportsWriteback=false`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`

## Policy summary

- allowed schemes: `https`
- allowed methods: `GET`
- synthetic allowlisted host: `api.fixture.invalid`
- redirect policy: `REJECT`, `maxRedirects=0`
- request timeout foundation default: `5000ms`
- max retry attempts: `3`
- max response bytes: `10485760`
- allowed content types: `application/json`, `text/csv`
- credential mode: `REFERENCE_ONLY`
- DNS resolution: `MODELED_ONLY`
- network access: disabled
- synthetic transport only

## Method enforcement

- GET accepted
- POST/PUT/PATCH/DELETE/CONNECT/TRACE/OPTIONS/HEAD rejected with `HTTP_METHOD_NOT_ALLOWED`
- no write method execution path

## SSRF model

- hostname normalization before modeled resolution
- allowlist enforcement for synthetic fixture hostnames
- private/loopback/link-local/multicast/unspecified/metadata rejection
- IPv4-mapped IPv6 bypass rejection
- DNS rebinding risk modeled without real DNS lookup

## Credential model

- `credentialRef` reference strings accepted (for example `secret://edge/http/example`)
- URL userinfo, plaintext username/password/bearer/API key rejected with `PLAINTEXT_CREDENTIAL_PROHIBITED`
- no `.env`, keychain, or credential store access

## Redirect policy

- all 3xx responses rejected with `HTTP_REDIRECT_REJECTED`
- redirect `Location` targets are validated but never followed

## Timeout/retry model

- retryable statuses modeled: `408`, `429`, `500`, `502`, `503`, `504`
- non-retryable statuses modeled: `400`, `401`, `403`, `404`
- deterministic exponential backoff with clamp
- no real sleep or network retry

## Response validation

- status/content-type/size checks
- JSON object/array accepted, scalar rejected in foundation
- CSV header/consistency checks
- formula-like CSV cells treated as plain text

## Synthetic transport proof

- validation-session JSON fixtures drive local evaluation
- transport mode fixed to `SYNTHETIC_TRANSPORT_ONLY`
- no socket, fetch, axios, curl, wget, or DNS lookup

## Validation results

- dry-run: `edge-c5-http-polling-readonly-dry-run: PASS` (72/72 cases)
- smoke: `edge-c5-http-polling-readonly-smoke: PASS`
- package validation: PASS
- boundary scan: PASS
- isolation result: PASS (`hard_fail_count=0`)
- shell evaluator reuses TypeScript policy/validator/retry/response logic via runtime TS transpilation loader

## Production limitations

- no real outbound HTTP endpoints
- no real DNS resolution
- no controlled pilot approval
- no production read-only approval
- no writeback enablement

## Acceptance result

- `HTTP_POLLING_READ_ONLY_FOUNDATION_ACCEPTED`
- `UFMS_EDGE_C5_02_HTTP_POLLING_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
