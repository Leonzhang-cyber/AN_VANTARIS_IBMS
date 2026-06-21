# ONE UMMS-R12 Read-only Frontend / UConsole Card Entry Report

## Baseline HEAD and latest tag

Baseline HEAD: `047134b3bd741c94287949b1e3b3e91d25f36995`

Latest published tag: `umms-r11-readonly-api-entry-skeleton-local-freeze-20260621`

## Changed files

- `AN_VANTARIS_IBMS-frontend/src/services/api/umms.ts`
- `AN_VANTARIS_IBMS-frontend/src/modules/umms/UmmsReadonlyOverview.vue`
- `AN_VANTARIS_IBMS-frontend/src/router/routes.ts`
- `AN_VANTARIS_ONE/registries/frontend-route-inventory.v1.json`
- `AN_VANTARIS_ONE/registries/package-route-enforcement.v1.json`
- `scripts/validation/build-one-frontend-route-inventory.py`
- `scripts/validation/validate-one-umms-r12-readonly-frontend-uconsole-card-entry.py`
- `ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_REPORT.md`

## Frontend / UConsole entry summary

UMMS-R12 adds a read-only UConsole-visible frontend entry at:

- `/one/umms/overview`

The entry displays:

- Package name: UMMS
- Full name: Unified Maintenance Management System
- Status: Stakeholder Review Ready
- Mode: Read-only
- Runtime: Disabled
- Latest archived tag: `umms-r11-readonly-api-entry-skeleton-local-freeze-20260621`
- Covered capabilities
- Safety posture
- Recommended next step: UMMS read-only frontend freeze / archive

The page exposes no write, approval, activation, deployment, workflow, work order runtime, PM execution, inventory transaction, vendor / contract / SLA runtime, evidence closure, HMI runtime/control, connector/device, EDGE/LINK runtime, or ONE Adapter actions.

Package-route metadata was updated only to keep the frozen static route inventory and package-route enforcement registry deterministic for the new read-only route. The new policy row remains metadata-only and explicitly does not claim runtime package enforcement implementation.

## API endpoints consumed

Frontend service methods use GET-only calls to:

- GET `/api/v1/one/umms/package-entry`
- GET `/api/v1/one/umms/stakeholder-review`
- GET `/api/v1/one/umms/readiness-summary`
- GET `/api/v1/one/umms/customer-core-functions`
- GET `/api/v1/one/umms/safety-posture`

No POST / PUT / PATCH / DELETE UMMS API client methods were added.

## Read-only fallback behavior

If the UMMS-R11 API is unavailable, the frontend shows:

`UMMS readiness data unavailable, read-only fallback active.`

Fallback data remains read-only and shows no runtime, write, approval, activation, deployment, workflow, work order, PM, inventory, vendor/contract/SLA, evidence closure, HMI, connector/device, EDGE/LINK, or ONE Adapter actions.

## Safety posture

- No DB write
- No workflow
- No approval execution
- No runtime activation
- No production activation
- No EDGE/LINK runtime call

## Validation commands

```bash
python3 scripts/validation/validate-one-umms-r12-readonly-frontend-uconsole-card-entry.py
PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-package-route-enforcement.py
PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py
PYTHONPYCACHEPREFIX=/tmp/one-r12-pycache python3 -m py_compile scripts/validation/validate-one-umms-r12-readonly-frontend-uconsole-card-entry.py scripts/validation/build-one-frontend-route-inventory.py
npm run type-check --prefix AN_VANTARIS_IBMS-frontend
npm run build --prefix AN_VANTARIS_IBMS-frontend
```

## Validation results

The UMMS-R12 validator is expected to confirm:

- UMMS-R12 report exists.
- Frontend UMMS read-only card/page entry exists.
- Frontend service consumes only GET UMMS-R11 endpoints.
- No POST / PUT / PATCH / DELETE UMMS API client methods were added.
- Card displays read-only, stakeholder review ready, runtime disabled, latest R11 tag, capability coverage, and safety posture.
- Card has no write/approval/activation/deployment/runtime action buttons.
- Fallback behavior is safe and read-only.
- No DB migration or DB write path was added.
- No ONE Adapter introduced.
- EDGE/LINK/Contracts/UFMS untouched.
- Prior UMMS archived PASS markers remain present.
- Package route enforcement, boundary baseline, Python compile, frontend type-check, and frontend build pass.

## PASS marker

`ONE_UMMS_R12_READONLY_FRONTEND_UCONSOLE_CARD_ENTRY_PASS`

## Confirmations

- No DB write was added.
- No runtime behavior was added.
- No POST / PUT / PATCH / DELETE API client methods were added.
- No write/approval/activation/deployment buttons were added.
- EDGE/LINK/Contracts/UFMS untouched.
- No ONE Adapter introduced.
- No push performed.

## Recommended next step

UMMS-R12 local freeze + optional tag plan.
