# ONE-UMMS-R2 Work Order / Asset / PM Domain Alignment Report

## Baseline HEAD and tags

- Baseline HEAD: `ec7ef2fc98cf6c7e1adc15d07b20d6210ee6389b`
- Published tags:
  - `airport-ga-readonly-stakeholder-review-local-freeze-20260621`
  - `airport-ga-readiness-projection-chain-local-freeze-20260621`

## Changed files

- `AN_VANTARIS_ONE/projections/umms-work-order-asset-pm-domain-alignment.v1.json`
- `AN_VANTARIS_ONE/registries/umms-work-order-asset-pm-domain-alignment-registry.v1.json`
- `ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_REPORT.md`
- `scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py`

## Projection summary

UMMS-R2 extracts Airport maintenance requirements into a generic VANTARIS ONE UMMS domain alignment model. UMMS remains a cross-industry maintenance management module. Airport remains an industry solution package and industry projection.

UMMS-R2 is read-only and projection-backed. It does not create work orders, execute PM schedules, write asset lifecycle state, reserve inventory, execute vendor/contract workflows, call EDGE/LINK runtime, or enable production/runtime activation.

## Generic UMMS domain object summary

The projection defines generic UMMS domain objects for fault cases, work orders, work-order triggers, assignments, status, evidence, assets, asset lifecycle records, asset location references, maintenance plans, PM schedules/tasks, checklists, future spare parts/inventory, future vendor/contract/SLA references, HMI locator references, and evidence references.

## Work Order domain model summary

The Work Order model defines generic fields for identity, type, source fault/alarm/event/trigger, asset/location, priority, severity, status, assignment, SLA, timestamps, evidence, HMI locator context, PM task linkage, spare parts, vendor, and contract references.

UMMS-R2 defines the domain alignment only. No work order creation or execution is implemented in UMMS-R2.

## Work Order lifecycle model summary

Future states are draft, triaged, assigned, accepted, in_progress, pending_parts, pending_vendor, pending_customer, resolved, verified, closed, and cancelled. All states have `executionAllowedInR2=false`.

## Work Order trigger alignment summary

LINK provides future trigger data including fault candidate, alarm/event, asset/location, severity, priority suggestion, source-system context, occurrence data, recommended action, evidence, and HMI locator references. UMMS owns work order lifecycle. UMMS-R2 does not consume live LINK runtime.

## Asset registry domain model summary

The asset model aligns generic asset identity, source-system mapping, device/point/tag context, location, vendor/model/serial, install/warranty/lifecycle status, maintenance/fault/work/PM history, HMI locator references, and evidence references.

UMMS-R2 does not write canonical Asset Graph. This is read-only domain alignment only.

## Asset lifecycle model summary

Future asset lifecycle states are planned, installed, commissioning, active, under_maintenance, degraded, retired, replaced, and decommissioned. All lifecycle states have `executionAllowedInR2=false`.

## Preventive maintenance domain model summary

The PM model defines plan, schedule, task, asset/location, maintenance type, frequency, runtime/event/condition thresholds, checklist, assignment, duration, spare parts, vendor/contract, completion/due dates, evidence, and work-order generation policy.

UMMS-R2 defines PM alignment only. No PM schedule execution or automatic work order generation is implemented in UMMS-R2.

## Airport-to-UMMS mapping summary

Airport Fault Cases map to UMMS FaultCase. Airport Maintenance Work Orders map to UMMS WorkOrder. Airport Assets & Topology map to UMMS Asset and AssetLocationReference. Airport Alarms & Events map to UMMS WorkOrderTrigger and FaultCase input. Airport Evidence Investigation maps to UMMS WorkOrderEvidence and UCDE EvidenceReference. Airport Reports map to maintenance report inputs. Airport HMI Locator Readiness maps to UMMS HmiLocatorReference. Airport Deployment Readiness maps to a future UMMS activation dependency.

## Customer core function alignment

UMMS-R2 aligns work order management, asset registry lifecycle tracking, PM scheduling, spare parts/inventory, vendor/contract management, Graphics HMI locator context, existing-system onboarding, engineer commissioning diagnostics, remote overseas deployment, and distributed independent installation to generic UMMS domains and future shared foundation dependencies.

## Shared EDGE/LINK/UCDE dependency map

EDGE dependencies are connector matrix, source-system onboarding profile, tag mapping and normalization, asset/location mapping preview, future runtime/event/condition signals, engineer diagnostics, HMI locator data foundation, and offline deployment readiness.

LINK dependencies are work-order trigger contract, source-system health contract, delivery readiness contract, asset/location reference contract, HMI drawing/symbol references, audit/evidence chain profile, delivery/ACK/retry/DLQ status, distributed topology contract, and remote support bundle contract.

UCDE dependencies are EvidenceRecord, WorkOrderEvidence, closure evidence, review evidence, audit trail, handoff package, and report evidence.

## Future UMMS roadmap

1. UMMS-R3 Manual Work Order Read-only Queue / Draft Model
2. UMMS-R4 Work Order Lifecycle State Model + Validation Gate
3. UMMS-R5 Preventive Maintenance Schedule Readiness
4. UMMS-R6 Spare Parts / Inventory Readiness
5. UMMS-R7 Vendor / Contract / SLA Readiness
6. UMMS-R8 UMMS + UCDE Evidence Closure Alignment
7. UMMS-R9 UMMS + Airport HMI Locator Binding Readiness
8. UMMS-R10 UMMS Stakeholder Review Package

## Source and behavior confirmations

- EDGE source modified: no
- LINK source modified: no
- Contracts source modified: no
- UFMS repository/source modified or accessed: no
- Workflow execution added: no
- Work order creation added: no
- PM schedule execution added: no
- Asset lifecycle write added: no
- Inventory transaction added: no
- Vendor/contract execution added: no
- DB write added: no
- Production activation added: no
- Runtime activation added: no
- ONE Adapter introduced: no

## Validation commands

- `git status -sb`
- `git log --oneline -14`
- `git tag --points-at HEAD`
- `grep -R "ONE_AIRPORT_GA_R10A_READINESS_PROJECTION_CHAIN_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv`
- `python3 scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py`
- `python3 scripts/validation/validate-one-airport-ga-r10a-readiness-projection-chain-freeze.py`
- `python3 scripts/validation/validate-one-airport-ga-r10-distributed-remote-deployment-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r6-link-integration-readiness.py`
- `python3 scripts/validation/validate-one-package-route-enforcement.py`
- `python3 scripts/validation/validate-one-boundaries.py`
- `python3 -m json.tool AN_VANTARIS_ONE/projections/umms-work-order-asset-pm-domain-alignment.v1.json`
- `python3 -m json.tool AN_VANTARIS_ONE/registries/umms-work-order-asset-pm-domain-alignment-registry.v1.json`

## Validation results

- UMMS-R2 validator: expected PASS
- GA-R10A through GA-R6 regression checks: expected PASS
- Package route enforcement: expected PASS
- Boundary baseline: expected PASS with existing non-blocking legacy warnings
- Projection JSON validation: expected PASS
- Registry JSON validation: expected PASS

## PASS marker

`ONE_UMMS_R2_WORK_ORDER_ASSET_PM_DOMAIN_ALIGNMENT_PASS`

## Known limitations

1. Domain alignment projection only.
2. No work order creation.
3. No PM schedule execution.
4. No asset lifecycle write.
5. No inventory transaction.
6. No vendor/contract execution.
7. No DB write.
8. No runtime or production activation.
9. No EDGE/LINK runtime call.
10. Existing boundary warnings remain non-blocking and unchanged.

## Recommended next tasks

1. UMMS-R3 Manual Work Order Read-only Queue / Draft Model
2. UMMS-R4 Work Order Lifecycle State Model + Validation Gate
3. UMMS-R5 Preventive Maintenance Schedule Readiness
4. UCDE-R4 Evidence Chain Alignment
5. Assets-R4 Asset/location projection refinement
6. UFMS-led shared foundation EDGE/LINK Airport ELV Phase 1
