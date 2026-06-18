# ONE Adapter Cancellation Summary

## 1. Decision

ONE Adapter is cancelled as an active VANTARIS ONE module.

## 2. Why Cancelled

- low practical engineering value
- duplicated responsibilities
- unnecessary middle layer
- boundary ambiguity and monolith risk

## 3. Affected Component

- `AN_VANTARIS_ONE/platform/one-adapter` (retained as deprecated historical documentation)

## 4. Function Reallocation Table

| Function | New owner |
| --- | --- |
| consumer boundary | governance/module manifest/UConsole |
| contract routing | Contracts + LINK |
| object mapping | EDGE + Contracts |
| identity preservation | EDGE + LINK + UCDE + DB |
| traceability preservation | LINK + UCDE + DB |
| external ingress | EDGE Fleet |
| delivery reference | LINK |
| evidence linkage | UCDE |

## 5. Manifest Status

- one-adapter status: `cancelled-a1`
- one-adapter is marked deprecated/cancelled with no active next task

## 6. Roadmap Status

- one-adapter active path removed from primary next-task chain
- current next task redirected to EDGE Fleet direct consumption stabilization

## 7. Remaining Historical Files

- `AN_VANTARIS_ONE/platform/one-adapter/module.manifest.draft.json`
- `AN_VANTARIS_ONE/platform/one-adapter/CONSUMER_CONTRACT_DRAFT.md`
- `AN_VANTARIS_ONE/platform/one-adapter/ONE_ADAPTER_A2_FOUNDATION_CONSUMER_GATE.md`

## 8. Next Task

`EDGE-FLEET-A1-CONSUMPTION-MODEL-DRAFT`
