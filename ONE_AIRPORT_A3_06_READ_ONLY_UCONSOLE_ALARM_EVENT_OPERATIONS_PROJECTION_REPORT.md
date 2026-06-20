# ONE-AIRPORT-A3-06 Read-Only UConsole Alarm/Event Operations Projection Report

## A. Baseline

- Workspace: `/Users/leon/Desktop/AN_VANTARIS_IBMS`
- Branch: `main`
- Baseline HEAD: `e0ac5b6 feat(one): add evidence investigation projection`
- Mode: read-only projection implementation
- UFMS live source was not accessed.

## B. Files changed

- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/__init__.py`
- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/enums.py`
- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/errors.py`
- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/models.py`
- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/projection.py`
- `AN_VANTARIS_ONE/uconsole_alarm_event_operations/validation.py`
- `AN_VANTARIS_ONE/registries/uconsole-alarm-event-operations-projection.v1.json`
- `AN_VANTARIS_ONE/industry_profiles/airport/uconsole_alarm_event_operations_projection.py`
- `AN_VANTARIS_ONE/industry_profiles/airport/projections/airport-uconsole-alarm-event-operations.v1.json`
- `AN_VANTARIS_ONE/tests/uconsole_alarm_event_operations/test_uconsole_alarm_event_operations_projection.py`
- `scripts/validation/validate-one-uconsole-alarm-event-operations-projection.py`
- `scripts/validation/_run_a3_06_uconsole_alarm_event_operations_projection.py`
- `ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_REPORT.md`

## C. Generic UConsole operations model

The generic package defines deterministic, read-only projection structures for:

- operations rows linking alarm/event candidates, asset-resolution rows, UFMS FaultCase candidates, WorkOrderIntent candidates and evidence investigation cases;
- operations cards for UConsole-ready queue and summary surfaces;
- filters, facets, pagination and deterministic digests;
- validation guards that keep API, frontend, database and downstream write counts disabled or zero.

No UConsole runtime route, frontend component, API handler, database migration, UFMS write, UMMS write, Evidence Center write or canonical model write was introduced.

## D. Airport operations summary

- Operations rows: 5
- Source systems: ACS, CCTV, PA, RAS, TEL
- Device evidence counts:
  - ACS: 129
  - RAS: 28
  - CCTV: 52
  - PA: 247
  - TEL: 14
- Total device evidence count: 470
- Decision-required rows: 5
- Blocked rows: 5
- Runtime-pending rows: 5
- Registry approval pending: 2
- Alias approval pending: 2
- Namespace review pending: 1

## E. Operations card summary

Seven operations cards are generated:

1. `ALARM_EVENT_QUEUE`
2. `FAULTCASE_CANDIDATE_QUEUE`
3. `WORKORDER_INTENT_QUEUE`
4. `EVIDENCE_INVESTIGATION_QUEUE`
5. `REVIEW_REQUIRED_SUMMARY`
6. `RUNTIME_PENDING_SUMMARY`
7. `SOURCE_SYSTEM_SUMMARY`

Each card is deterministic, read-only and UConsole-ready as projection data only.

## F. Boundary confirmation

- API enabled: false
- Frontend enabled: false
- Database writes: 0
- Canonical writes: 0
- UFMS FaultCases created: 0
- WorkOrderIntents created: 0
- WorkOrders created: 0
- Evidence Center writes: 0
- UMMS writes: 0
- ONE Work Management writes: 0
- Runtime alarm observations: 0
- Customer asset identifiers exposed: false
- Cross-industry projection: true
- Airport-specific contract model: false

## G. Tests and PASS counts

- Focused A3-06 unit tests: 9 tests PASS
- A3-06 validator: 41 PASS checks
- Deterministic runner: PASS
- Repeated generation byte-identical: PASS

## H. Final commit and working tree

Pending at report creation; final commit and working tree confirmation are recorded in the assistant handoff after validation and commit.

## I. Summary JSON

```json
{
  "operationsRowCount": 5,
  "operationsCardCount": 7,
  "alarmEventCandidateCount": 5,
  "resolutionRowCount": 5,
  "faultCaseCandidateCount": 5,
  "workOrderIntentCandidateCount": 5,
  "investigationCaseCount": 5,
  "totalDeviceEvidenceCount": 470,
  "decisionRequiredCount": 5,
  "reviewRequiredRowCount": 5,
  "blockedRowCount": 5,
  "runtimePendingCount": 5,
  "registryApprovalPendingCount": 2,
  "aliasApprovalPendingCount": 2,
  "namespaceReviewPendingCount": 1,
  "assetResolutionRequiredCount": 5,
  "faultCaseReviewRequiredCount": 5,
  "workOrderIntentReviewRequiredCount": 5,
  "evidenceInvestigationReviewRequiredCount": 5,
  "runtimeAlarmObservedCount": 0,
  "ufmsFaultCaseCreatedCount": 0,
  "workOrderIntentCreatedCount": 0,
  "workOrderCreatedCount": 0,
  "evidenceCenterWriteCount": 0,
  "ummsWriteCount": 0,
  "oneWorkManagementWriteCount": 0,
  "canonicalWriteCount": 0,
  "databaseWriteCount": 0,
  "apiEnabled": false,
  "frontendEnabled": false,
  "containsCustomerAssetIdentifiers": false,
  "crossIndustry": true,
  "airportSpecific": false
}
```

## J. PASS marker

`ONE_AIRPORT_A3_06_READ_ONLY_UCONSOLE_ALARM_EVENT_OPERATIONS_PROJECTION_PASS`
