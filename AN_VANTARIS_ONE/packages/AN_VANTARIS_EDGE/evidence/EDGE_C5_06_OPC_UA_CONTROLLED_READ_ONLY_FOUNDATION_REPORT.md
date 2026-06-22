# EDGE C5-06 OPC UA Controlled Read-only Foundation Report

- **Task:** UFMS-EDGE-C5-06
- **Baseline:** `380056d` feat(edge): add bacnet ip readonly foundation
- **Readiness key:** `UFMS_EDGE_C5_06_OPC_UA_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
- **Acceptance result:** `OPC_UA_READ_ONLY_FOUNDATION_ACCEPTED`

## Scope

Controlled OPC UA read-only foundation with synthetic transport only. No real OPC UA SDK, TCP sockets, DNS, endpoint discovery, credential resolution, or trust-store writes.

## Endpoint policy

- Allowlisted endpoint: `opc.tcp://opcua.fixture.invalid:4840`
- Scheme `opc.tcp` required; userinfo/query/fragment rejected
- Localhost, loopback, private, link-local, multicast, unspecified, metadata, and IPv4-mapped bypass rejected
- `endpointDiscoveryMode=MODELED_ONLY`

## Security policy and message mode

- Allowed SecurityPolicy: Basic256Sha256, Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaPss
- Allowed MessageSecurityMode: SIGN, SIGN_AND_ENCRYPT
- SecurityPolicy None, legacy Basic128Rsa15/Basic256, and MessageSecurityMode NONE rejected
- No SecureChannel handshake or certificate chain validation in Foundation phase

## Identity and certificate reference model

- `credentialMode=REFERENCE_ONLY`, `certificateMode=REFERENCE_ONLY`
- Accepts `secret://`, `cert://`, `key://`, `fingerprint://` reference strings only
- Plaintext username/password/token and inline PEM certificate/private key rejected
- Anonymous identity prohibited

## Server identity model

- Server fingerprint reference required (`fingerprint://edge/opcua/server/example`)
- Hostname and application URI verification modeled
- Trust-on-first-use and automatic trust approval prohibited
- No trust-store writes

## Service enforcement

- Allowed: BROWSE, BROWSE_NEXT, READ, TRANSLATE_BROWSE_PATHS_TO_NODE_IDS
- Denied: WRITE, CALL, node management, subscriptions, monitored items, HISTORY_UPDATE
- HistoryRead disabled by default

## Namespace and NodeId policy

- Allowed namespace indexes: 0, 2
- Allowed NodeId types: NUMERIC, STRING
- Synthetic fixture nodes: `ns=0;i=2258`, `ns=2;i=1001`, `ns=2;i=1002`, `ns=2;s=Area1.Sensor1`, `ns=2;s=Area1.Sensor2`
- Structured prefix boundaries prevent component bypass (e.g. `Area10.Sensor1` vs `Area1.Sensor`)

## Read and browse limits

- `maxNodesPerRead=100`, `maxNodesPerBrowse=100`, `maxBrowseDepth=16`
- Attribute allowlist enforced; index range validated
- Synthetic continuation points only

## Response, DataValue, and Variant validation

- Request handle, service, NodeId, and attribute consistency enforced
- Good StatusCode required for value acceptance
- Bad and Uncertain StatusCodes rejected (`rejectUncertainStatusCodes=true`)
- Variant type, array length, string length, and timestamp validation enforced

## Retry and backoff

- Retryable: TIMEOUT, TRANSPORT_RETRYABLE, SECURE_CHANNEL_CLOSED, SESSION_CLOSED, SERVER_BUSY
- Non-retryable: POLICY_VIOLATION, ENDPOINT_NOT_ALLOWED, SECURITY_POLICY_NOT_ALLOWED, CERTIFICATE_MISMATCH, NODE_ID_NOT_ALLOWED, WRITE_SERVICE_PROHIBITED, MALFORMED_RESPONSE
- Deterministic exponential backoff with clamp; no sleep or real retry

## Synthetic transport proof

- `executeSyntheticOpcUaFixture()` validates request policy gates and synthetic response only
- Output transport mode: `SYNTHETIC_TRANSPORT_ONLY`

## No-network proof

- No OPC UA SDK (`node-opcua`), TCP socket creation, DNS lookup, endpoint discovery network calls, credential resolution, or trust-store writes in connector modules

## Connector blocked state

OPC UA connector remains:

- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `realConnectivityEnabled=false`
- `supportsWriteback=false`
- `readOnlyEnforcementGate=DEFERRED`

## Validation

```bash
npm run typecheck:edge
bash AN_VANTARIS_EDGE/scripts/validation/edge-c5-opc-ua-readonly-dry-run.sh
bash AN_VANTARIS_EDGE/scripts/validation/edge-c5-opc-ua-readonly-smoke.sh
bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh
bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh
bash scripts/validate-ufms-ibms-isolation.sh
```

## Limitations

- Foundation models security and session boundaries only; no production SecureChannel or Session establishment
- HistoryRead, subscriptions, and monitored items deferred to future phases
- Trust store and certificate chain validation not implemented
- No pilot or production approval in this phase

## Final decision

`OPC_UA_READ_ONLY_FOUNDATION_ACCEPTED` — controlled read-only foundation ready for synthetic validation only; connector remains blocked for production use.
