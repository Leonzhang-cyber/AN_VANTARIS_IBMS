# EDGE C5-07 Six-Connector Read-only Foundation Freeze Report

- **Task:** UFMS-EDGE-C5-07
- **Baseline:** `1267381` feat(edge): add opc ua readonly foundation
- **Readiness key:** `UFMS_EDGE_C5_07_SIX_CONNECTOR_READ_ONLY_FOUNDATION_FREEZE_PASS`
- **Freeze result:** `SIX_CONNECTOR_READ_ONLY_FOUNDATION_FREEZE_VERIFIED`

## Six-connector commit chain

| Connector | Phase | Commit |
|-----------|-------|--------|
| file | C5-01 | `d758e84` |
| http | C5-02 | `0f63917` |
| snmp | C5-03 | `0a18fe0` |
| modbus | C5-04 | `3032027` |
| bacnet | C5-05 | `380056d` |
| opcua | C5-06 | `1267381` |

## Connector inventory

Unified freeze manifest: `deploy/offline-bundle/connector-enablement/CONNECTOR_READ_ONLY_FOUNDATION_FREEZE.edge.json`

All six connectors retain foundation-only synthetic fixtures with blocked production enablement.

## Common policy mapping

Documented in `CONNECTOR_READ_ONLY_POLICY_COMMON_FIELDS.edge.json` with per-protocol field mappings (HTTP `allowedMethods`, SNMP `allowedOperations`, Modbus function codes, BACnet/OPC UA services, File extensions and mutation flags).

## Read operation matrix

| Connector | Allowed read operations |
|-----------|-------------------------|
| file | READ_FILE, PARSE_JSON, PARSE_CSV |
| http | GET |
| snmp | GET, GETNEXT, GETBULK |
| modbus | FC01, FC02, FC03, FC04 |
| bacnet | READ_PROPERTY, READ_PROPERTY_MULTIPLE |
| opcua | BROWSE, BROWSE_NEXT, READ, TRANSLATE_BROWSE_PATHS_TO_NODE_IDS |

## Write denial matrix

| Connector | Prohibited write operations |
|-----------|----------------------------|
| file | MOVE, DELETE, RENAME, CHMOD, WRITE |
| http | POST, PUT, PATCH, DELETE |
| snmp | SET, INFORM, TRAP_SEND |
| modbus | FC05, FC06, FC15, FC16, FC22, FC23 |
| bacnet | WRITE_PROPERTY, WRITE_PROPERTY_MULTIPLE, DCC, REINITIALIZE_DEVICE, CREATE_OBJECT, DELETE_OBJECT |
| opcua | WRITE, CALL, ADD_NODES, DELETE_NODES, CREATE_SUBSCRIPTION, CREATE_MONITORED_ITEMS, HISTORY_UPDATE |

## Error taxonomy

Consolidated in `CONNECTOR_ERROR_TAXONOMY.edge.json` mapping connector-specific **runtime** error codes to shared categories without renaming existing error codes.

### C5-07A exact-code alignment (UFMS-EDGE-C5-07A)

Independent verify (`UFMS-EDGE-C5-07-CURSOR-INDEPENDENT-VERIFY`) found taxonomy **alias drift**: mapped keys such as `FILE_PATH_TRAVERSAL`, `FILE_SIZE_EXCEEDED`, `FILE_DUPLICATE_DETECTED`, and `SNMP_WRITE_PROHIBITED` did not match runtime tokens emitted by connector source.

C5-07A corrected mappings to real runtime codes only, for example:

| Removed alias | Runtime code used |
|---------------|-------------------|
| `FILE_PATH_TRAVERSAL` | `PATH_TRAVERSAL_DETECTED` |
| `FILE_SIZE_EXCEEDED` | `FILE_TOO_LARGE` |
| `FILE_DUPLICATE_DETECTED` | `DUPLICATE_DETECTED` |
| `SNMP_WRITE_PROHIBITED` | `SNMP_SET_NOT_ALLOWED` |

Additional File/HTTP alias removals include `FILE_PATH_NOT_ALLOWED` → `PATH_OUTSIDE_ALLOWLIST`, `FILE_SYMLINK_REJECTED` → `SYMLINK_REJECTED`, and HTTP SSRF/credential/response codes aligned to `SSRF_*`, `PLAINTEXT_CREDENTIAL_PROHIBITED`, `MALFORMED_JSON_RESPONSE`, and `HTTP_STATUS_NOT_ACCEPTED`.

The freeze verifier now scans each mapped code as a quoted token in connector source **or** frozen policy/acceptance artifacts. Fictional or alias-only codes fail verification. No connector runtime behavior changed; no error codes were renamed in source.

## Evidence index

Indexed in `CONNECTOR_EVIDENCE_INDEX.edge.json`:

- EDGE_C5_01 through EDGE_C5_06 foundation reports
- EDGE_C5_07 freeze report (this document)

## Regression summary

Full per-connector dry-run regression (once per C5-07 validation):

- File: 53/53
- HTTP: 72/72
- SNMP: 81/81
- Modbus: 104/104
- BACnet: 124/124
- OPC UA: 152/152
- **Total: 586/586**

## Consolidation validation

```bash
npm run typecheck:edge
bash AN_VANTARIS_EDGE/scripts/validation/edge-c5-connector-foundation-consolidation-dry-run.sh
bash AN_VANTARIS_EDGE/scripts/validation/edge-c5-connector-foundation-consolidation-smoke.sh
bash AN_VANTARIS_EDGE/deploy/offline-bundle/scripts/verify-connector-readonly-foundation-freeze-edge.sh
```

C5-07A consolidation dry-run: **126/126** (adds taxonomy runtime-code existence and alias/fictional rejection cases). Six-connector per-connector regression baseline remains **586/586** unchanged.

## Blocked-state proof

All six matrix entries remain:

- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `realConnectivityEnabled=false`
- `supportsWriteback=false`
- `readOnlyEnforcementGate=DEFERRED`
- `syntheticFixtureOnly=true`

## Synthetic-only / no-network proof

Network-capable connectors enforce `syntheticTransportOnly=true` and `networkAccessAllowed=false` in policy (File uses validation-session local read with `networkFilesystemAllowed=false`).

## Known non-blocking limitations

**File:** evaluator TS loader complexity; no real directory watch or production quarantine.

**HTTP:** redirect Location SSRF not independently parsed; response size policy is foundation-only; no real TLS/HTTP client.

**SNMP:** no real SNMPv3 engine authPriv or engine ID; no UDP or walk implementation.

**Modbus:** MBAP length is simplified foundation model; no real TCP client or connection recovery.

**BACnet:** APDU size uses deterministic estimate; no UDP, Who-Is, BBMD, or FDR.

**OPC UA:** synthetic trust model is not production certificate trust; maxRequestBytes not always auto-bound; no SecureChannel, Session, or trust store.

## Next phase boundary

C5 Foundation Freeze completes unified audit and regression verification only. It does **not** enable:

- production readiness
- controlled pilot approval
- real connector connectivity
- field deployment

## Final decision

`SIX_CONNECTOR_READ_ONLY_FOUNDATION_FREEZE_VERIFIED` — C5 read-only foundation layer frozen for six connectors; all remain blocked for production use.

C5-07A adds `ERROR_TAXONOMY_RUNTIME_CODES_VERIFIED` — taxonomy mappings use exact runtime tokens; blocked state and six-connector behavior unchanged; no commits in this correction pass.
