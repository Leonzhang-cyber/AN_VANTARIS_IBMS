# ONE-UMMS-R6 Spare Parts / Inventory Readiness Report

## Baseline HEAD and tags

Baseline HEAD: `849b4ee41df7da498897e7b7849d45353b7f409e`

Published tags:

- airport-ga-readonly-stakeholder-review-local-freeze-20260621
- airport-ga-readiness-projection-chain-local-freeze-20260621
- umms-r2-work-asset-pm-domain-alignment-local-freeze-20260621
- umms-r3-manual-work-order-draft-model-local-freeze-20260621
- umms-r4-work-order-lifecycle-validation-gate-local-freeze-20260621
- umms-r5-preventive-maintenance-schedule-readiness-local-freeze-20260621

## Changed files

- `AN_VANTARIS_ONE/projections/umms-spare-parts-inventory-readiness.v1.json`
- `AN_VANTARIS_ONE/registries/umms-spare-parts-inventory-readiness-registry.v1.json`
- `ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_REPORT.md`
- `scripts/validation/validate-one-umms-r6-spare-parts-inventory-readiness.py`

## Projection summary

UMMS-R6 defines generic spare parts and inventory readiness for VANTARIS ONE UMMS. It is read-only and projection-backed. UMMS remains a cross-industry maintenance management module; Airport remains the first industry use case, not UMMS core identity.

## Spare part catalog model summary

The spare part catalog model defines future catalog fields such as spare part reference, part number, category, manufacturer, model compatibility, vendor/contract references, substitute parts, shelf-life, warranty tracking, evidence references, and review status. Catalog activation remains disabled.

## Inventory item model summary

The inventory item model defines future item and quantity fields such as location references, quantity on hand, available, reserved, on order, min/max stock levels, reorder point, unit cost, batch/serial data, expiry, warranty, stock status, evidence, and validation status. No quantity mutation is implemented.

## Inventory location model summary

The inventory location model defines future warehouse, store room, bin, site, building, room, zone, access control, environmental, hazardous-area, responsible-role, stock count, and evidence readiness fields. No location creation or update is implemented.

## Spare part requirement model summary

The spare part requirement model defines future requirement references from work orders, PM tasks, assets, and fault cases to required parts, quantities, priority, reservation need, substitution, vendor support, contract references, and evidence. No reservation, issue, deduction, or consumption is implemented.

## Work order spare part readiness summary

Work order spare part readiness captures future part requirements, availability, shortage, reservation, issue, return, substitution, vendor support, evidence, and inventory gate status. No work order spare part consumption is implemented.

## PM spare part readiness summary

PM spare part readiness captures future PM plan, schedule, task, asset, location, required parts, recommended quantities, minimum stock dependencies, reservation policy, availability, shortage risk, vendor lead-time risk, contract coverage, and evidence. No PM spare part reservation or consumption is implemented.

## Inventory policy model summary

UMMS-R6 models future minimum stock, reorder point, reservation, issue, return, stock count, expiry, substitution, vendor lead-time, and critical spares policies. Every policy has `executionAllowedInR6` set to false.

## Procurement suggestion readiness summary

Procurement suggestion readiness captures future shortage, minimum stock breach, forecast demand, vendor/contract reference, lead time, recommended quantity, estimated cost, approval need, purchase order allowance, and evidence. Purchase order allowance remains false and no procurement request or purchase order execution is implemented.

## Inventory validation gate model summary

Inventory validation gates include catalog completeness, item reference, location reference, minimum stock, work order requirement, PM requirement, reservation, issue, return, substitute part, vendor/contract, procurement suggestion, evidence, stock count, and expiry/warranty readiness gates.

## Asset spare part linkage model summary

Asset spare part linkage defines future asset, system, discipline, location, HMI locator, recommended/critical/PM/work-order spare part references, vendor, contract, warranty, evidence, and lifecycle context. UMMS-R6 does not write canonical Asset Graph.

## Airport-to-inventory mapping summary

Airport sources are mapped read-only into UMMS inventory readiness: assets/topology to asset-to-spare-part linkage, maintenance work orders to work order requirements, PM readiness to PM requirements, fault cases to critical spare risk context, evidence investigation to inventory evidence, HMI locator readiness to asset/location inventory context, and reports to inventory readiness reporting.

## Customer core function alignment

UMMS-R6 covers all customer core functions as readiness only: work order management, asset registry, preventive maintenance scheduler, spare parts/inventory management, vendor/contract management, graphics HMI equipment location, existing system onboarding, engineer commissioning diagnostics, remote overseas deployment, and distributed independent installation.

## Shared EDGE/LINK/UCDE dependency map

EDGE dependencies are listed only: asset/location mapping preview, tag mapping and normalization, HMI locator data foundation, engineer diagnostics, and future condition signals for critical spares planning.

LINK dependencies are listed only: source-system health contract, delivery readiness contract, asset/location reference contract, work-order trigger contract, audit/evidence chain profile, delivery/ACK/retry/DLQ status, and distributed topology contract.

UCDE dependencies are listed only: spare part catalog evidence, inventory item evidence, reservation evidence, issue/return evidence, procurement suggestion evidence, work order spare part evidence, PM spare part evidence, audit trail, and report evidence.

## Future UMMS roadmap

1. UMMS-R6A Local Freeze + Optional Tag Plan
2. UMMS-R7 Vendor / Contract / SLA Readiness
3. UMMS-R8 UMMS + UCDE Evidence Closure Alignment
4. UMMS-R9 UMMS + Airport HMI Locator Binding Readiness
5. UMMS-R10 UMMS Stakeholder Review Package

## Source and behavior confirmations

- EDGE source modified: no
- LINK source modified: no
- Contracts source modified: no
- UFMS source accessed or modified: no
- Inventory transaction added: no
- Stock reservation added: no
- Stock deduction added: no
- Stock return added: no
- Procurement execution added: no
- Purchase order execution added: no
- Work order spare part consumption added: no
- DB write added: no
- Workflow execution added: no
- Production activation added: no
- Runtime activation added: no
- ONE Adapter introduced: no

## Validation commands

- `git status -sb`
- `git log --oneline -14`
- `git tag --points-at HEAD`
- `rg "ONE_UMMS_R5A_LOCAL_FREEZE_AND_OPTIONAL_TAG_PLAN_PASS" -g '!node_modules' -g '!.git' -g '!.venv' -g '!venv'`
- `python3 scripts/validation/validate-one-umms-r6-spare-parts-inventory-readiness.py`
- `python3 scripts/validation/validate-one-umms-r5a-local-freeze.py`
- `python3 scripts/validation/validate-one-umms-r5-preventive-maintenance-schedule-readiness.py`
- `python3 scripts/validation/validate-one-umms-r4a-local-freeze.py`
- `python3 scripts/validation/validate-one-umms-r4-work-order-lifecycle-state-validation-gate.py`
- `python3 scripts/validation/validate-one-umms-r3a-local-freeze.py`
- `python3 scripts/validation/validate-one-umms-r3-manual-work-order-readonly-queue-draft-model.py`
- `python3 scripts/validation/validate-one-umms-r2a-local-freeze.py`
- `python3 scripts/validation/validate-one-umms-r2-work-order-asset-pm-domain-alignment.py`
- `PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-package-route-enforcement.py`
- `PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py`
- `python3 -m json.tool AN_VANTARIS_ONE/projections/umms-spare-parts-inventory-readiness.v1.json`
- `python3 -m json.tool AN_VANTARIS_ONE/registries/umms-spare-parts-inventory-readiness-registry.v1.json`

## Validation results

- UMMS-R6 validator: PASS
- UMMS-R5A validator: PASS
- UMMS-R5 validator: PASS
- UMMS-R4A validator: PASS
- UMMS-R4 validator: PASS
- UMMS-R3A validator: PASS
- UMMS-R3 validator: PASS
- UMMS-R2A validator: PASS
- UMMS-R2 validator: PASS
- Package route enforcement: PASS
- Boundary baseline: PASS with existing non-blocking legacy warnings
- Projection JSON validation: PASS
- Registry JSON validation: PASS

## PASS marker

`ONE_UMMS_R6_SPARE_PARTS_INVENTORY_READINESS_PASS`

## Known limitations

UMMS-R6 is readiness-only. It does not create or update spare parts, mutate quantities, reserve stock, issue stock, return stock, create procurement requests, create purchase orders, write database records, run workflows, or activate production/runtime behavior.

## Recommended next tasks

1. UMMS-R6A Local Freeze + Optional Tag Plan
2. UMMS-R7 Vendor / Contract / SLA Readiness
3. UMMS-R8 UMMS + UCDE Evidence Closure Alignment
4. UMMS-R9 UMMS + Airport HMI Locator Binding Readiness
5. UMMS-R10 UMMS Stakeholder Review Package
