# ONE-AIRPORT-GA-R2 Read-Only API Local Smoke and Contract Regression Report

## Baseline

- Baseline HEAD before GA-R2: `c78fb35190c76027115b4bb92fc8322bf07b73c7`
- GA-R1 commit reference: `c78fb35190c76027115b4bb92fc8322bf07b73c7`
- Previous GA RC tag: `airport-international-ga-ready-readonly-rc-20260620`
- Scope: validation, smoke, contract regression, and report only.
- Push performed: no.

## Routes tested

| Endpoint key | Method | Route |
|---|---:|---|
| AIRPORT_OVERVIEW | GET | `/api/v1/one/airport/console/overview` |
| SYSTEMS_INTEGRATION_HEALTH | GET | `/api/v1/one/airport/console/systems-integration-health` |
| ASSETS_TOPOLOGY | GET | `/api/v1/one/airport/console/assets-topology` |
| ALARMS_EVENTS | GET | `/api/v1/one/airport/console/alarms-events` |
| FAULT_CASES | GET | `/api/v1/one/airport/console/fault-cases` |
| MAINTENANCE_WORK_ORDERS | GET | `/api/v1/one/airport/console/maintenance-work-orders` |
| EVIDENCE_INVESTIGATION | GET | `/api/v1/one/airport/console/evidence-investigation` |
| REPORTS | GET | `/api/v1/one/airport/console/reports` |

## GET smoke result matrix

| Check | Result |
|---|---|
| 8 GET routes return HTTP 200 | PASS |
| 8 GET routes return JSON | PASS |
| `platform = VANTARIS ONE` | PASS |
| `industryProjection = airport` | PASS |
| `readOnly = true` | PASS |
| `productionActivation = false` | PASS |
| `runtimeActivation = false` | PASS |
| `dbWrite = false` | PASS |
| `approvalExecution = false` | PASS |
| `customerIdentifierLeakage = false` | PASS |
| Source mapping present | PASS |

## Non-GET rejection matrix

| Method | Routes tested | Expected | Result |
|---|---:|---|---|
| POST | 8 | 404/405 and no business success response | PASS |
| PUT | 8 | 404/405 and no business success response | PASS |
| PATCH | 8 | 404/405 and no business success response | PASS |
| DELETE | 8 | 404/405 and no business success response | PASS |

## Response contract regression matrix

| Contract check | Result |
|---|---|
| A7 frozen route paths unchanged | PASS |
| A7 mock route paths unchanged | PASS |
| Response top-level payload keys unchanged | PASS |
| Read-only safety flags present | PASS |
| Artifact-backed behavior retained | PASS |
| `backend-route-inventory.v1.json` matches implemented GA-R1 routes | PASS |
| GA-R1 report route list matches implemented routes | PASS |

## Read-only safety matrix

| Boundary | Result |
|---|---|
| No DB migration | PASS |
| No DB write | PASS |
| No runtime activation | PASS |
| No production API activation | PASS |
| No approval decision execution | PASS |
| No real device connection | PASS |
| No UFMS repository/source access | PASS |
| No frontend modification | PASS |
| No EDGE/LINK/Contracts modification | PASS |

## Artifact/projection source verification

Each route source mapping is checked against `AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-read-only-api-skeleton.v1.json`.

Result: PASS.

## Customer identifier leakage check

Checked response serialization for:

- `customerAssetIdentifier`
- `"assetId"`
- `"deviceId"`
- local absolute `/Users/` paths

Result: PASS.

## Boundary validation result

Expected marker: `ONE_BOUNDARY_BASELINE_PASS`

Existing legacy warnings remain non-blocking:

- `A4-BND-002` legacy device model combines canonical identity and EDGE connector concerns.
- `A4-BND-009` reports local audit persistence outside Governance & Security.
- `A4-BND-011` UMMS skeleton defines generic WorkOrder records outside ONE Work Management.
- `A4-BND-012` UCDE skeleton provides EvidenceRecord data outside Evidence Center.

No new P0 boundary issue is introduced by GA-R2.

## Validation commands

- `git status -sb`
- `git log --oneline -8`
- `git diff --name-only HEAD~1..HEAD`
- `AN_VANTARIS_IBMS-backend/.venv/bin/python -m unittest discover -s AN_VANTARIS_ONE/tests/airport_ga_readonly_api -p 'test_*.py'`
- `AN_VANTARIS_IBMS-backend/.venv/bin/python scripts/validation/validate-one-airport-ga-r2-readonly-api-smoke-regression.py`
- `AN_VANTARIS_IBMS-backend/.venv/bin/python scripts/validation/validate-one-airport-ga-readonly-api-routes.py`
- `python3 scripts/validation/validate-one-airport-read-only-api-skeleton.py`
- `python3 scripts/validation/validate-one-airport-read-only-api-response-contract.py`
- `python3 scripts/validation/validate-one-airport-read-only-api-mock-route-contract.py`
- `python3 scripts/validation/validate-one-airport-read-only-api-release-gate.py`
- `python3 scripts/validation/validate-one-airport-international-ga-final-verification.py`
- `python3 scripts/validation/validate-one-backend-route-inventory.py`
- `python3 scripts/validation/validate-one-boundaries.py`
- `grep -R "ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS" .`

## PASS markers

- `ONE_AIRPORT_GA_R1_READONLY_API_ROUTE_IMPLEMENTATION_PASS`
- `ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS`
- `ONE_AIRPORT_A7_01_READ_ONLY_API_SKELETON_FOUNDATION_PASS`
- `ONE_AIRPORT_A7_02_READ_ONLY_API_RESPONSE_CONTRACT_AND_VALIDATION_GATE_PASS`
- `ONE_AIRPORT_A7_03_READ_ONLY_API_MOCK_ROUTE_CONTRACT_AND_LOCAL_SMOKE_GATE_PASS`
- `ONE_AIRPORT_A7_04_READ_ONLY_API_IMPLEMENTATION_RELEASE_GATE_PASS`
- `ONE_AIRPORT_GA_04_INTERNATIONAL_GA_FINAL_LOCAL_VERIFICATION_AND_OPTIONAL_RELEASE_TAG_PLAN_PASS`
- `ONE_BACKEND_ROUTE_INVENTORY_PASS`
- `ONE_BOUNDARY_BASELINE_PASS`

## Final confirmation

PASS marker: `ONE_AIRPORT_GA_R2_READONLY_API_LOCAL_SMOKE_AND_CONTRACT_REGRESSION_PASS`

Push performed: no.

