# ONE-AIRPORT-GA-R9 Graphics HMI Equipment Locator Readiness Report

## Baseline HEAD and tag

- Baseline HEAD: `30ba3536e45feb9c7030c1625f4338688f386308`
- Baseline tag: `airport-ga-readonly-stakeholder-review-local-freeze-20260621`
- GA-R8 dependency: `ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS`
- Branch state before GA-R9: `main...origin/main [ahead 3]`

## Changed files

- `AN_VANTARIS_ONE/projections/airport-graphics-hmi-equipment-locator-readiness.v1.json`
- `AN_VANTARIS_ONE/registries/airport-graphics-hmi-equipment-locator-readiness-registry.v1.json`
- `ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_REPORT.md`
- `scripts/validation/validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py`

## Projection summary

GA-R9 adds a VANTARIS ONE-side, read-only Airport Graphics HMI equipment locator readiness projection. It defines future asset-to-location-to-drawing-to-HMI-symbol mapping requirements, alarm/event/fault/work-order locator chains, asset-location mapping validation needs, HMI locator use cases, customer function impact, EDGE/LINK shared foundation requirements, and future rendering dependencies.

GA-R9 does not implement Graphics HMI runtime execution, customer drawing upload, customer-specific rendering, BIM runtime integration, equipment control, device connection, connector execution, EDGE runtime calls, LINK runtime calls, backend behavior, frontend behavior, UConsole behavior, or DB writes.

## Locator reference model summary

The locator reference model defines future references for `assetRef`, `locationRef`, `systemRef`, `equipmentRef`, `drawingRef`, `floorPlanRef`, `zoneRef`, `floorRef`, `roomRef`, `hmiSymbolRef`, `topologyNodeRef`, optional `bimObjectRef`, `evidenceRef`, `workOrderRef`, `faultCaseRef`, and `alarmEventRef`.

The model keeps canonical asset/location identity in the ONE Asset Graph / Layer 3 and contracts, while future rendering and symbol resolution remain future package capabilities.

## Location hierarchy model summary

The projection defines the future location hierarchy fields: site, terminal, building, level, floor, zone, room, area, equipment space, coordinate system, x/y/z coordinates, optional geo reference, drawing layer, and HMI symbol layer.

GA-R9 defines the readiness model only. No customer-specific location data is loaded.

## Drawing and symbol requirement summary

Future drawing and symbol fields include drawing reference, type, version, discipline, floor-plan reference, symbol-library reference, HMI symbol reference, symbol type/label/status/coordinates/layer, asset reference, location reference, last review time, and review status.

Drawing types include 2D floor plan, ELV system schematic, system topology, future optional single-line diagram, and future optional BIM view.

No drawing upload or rendering is implemented in GA-R9.

## Locator chain requirement summary

GA-R9 defines readiness chains for:

1. Alarm to Asset to Location to Drawing to HMI Symbol
2. Event to Asset to Location to Drawing to HMI Symbol
3. Fault Case to Asset to Location to HMI Symbol
4. Work Order to Asset to Location to HMI Symbol
5. Asset Registry to Location to Drawing to HMI Symbol
6. Preventive Maintenance Task to Asset to Location to HMI Symbol
7. Spare Part to Asset to Location, future optional
8. Vendor / Contract to Asset to Location, future optional
9. Evidence Record to Asset / Fault / Work Order to Location

## Asset/location mapping requirement summary

The projection defines future asset-location mapping fields for asset, source-system, connector, device, point, tag, location, drawing, symbol, topology, optional BIM, mapping status, confidence, review status, and risk flags.

Validation requirements include missing asset, location, drawing, and HMI symbol references; duplicate symbols; conflicting locations; stale drawing versions; and unreviewed mappings.

## HMI locator use case readiness

GA-R9 covers read-only readiness for locating equipment from alarms, events, fault cases, work orders, asset registry records, PM tasks, same-zone equipment, evidence source context, engineer review of unmapped equipment, and supervisor review of location confidence.

## Customer core function locator impact

GA-R9 maps locator readiness to work order management, asset registry lifecycle tracking, preventive maintenance scheduling, spare parts and inventory, vendor/contract management, Graphics HMI equipment location, existing-system onboarding, engineer commissioning diagnostics, remote overseas deployment, and distributed independent installation.

## EDGE/LINK shared foundation interface requirements

Future EDGE requirements include asset/location capture from connector mapping, HMI symbol and drawing mapping support, source tag to asset/location mapping preview, asset-location diagnostics, HMI locator data foundation, sample payloads with locator references, normalization preview with locator references, connector validation for missing references, and engineer commissioning output for locator readiness.

Future LINK requirements include asset/location reference contracts, HMI symbol and drawing reference fields, source-system health with locator mapping status, delivery envelopes with asset/location references, work-order triggers with asset/location/HMI references, evidence chains with asset/location context, mapping profile contracts, distributed topology references, support bundle locator readiness summaries, and audit events for mapping review status.

## Future rendering dependency model

Future rendering dependencies include a 2D floor-plan renderer, symbol library, equipment locator overlay, asset topology graph, system topology view, alarm/event highlight overlay, work-order location overlay, evidence-linked location view, future optional BIM integration, and future optional mobile locator view.

GA-R9 does not implement rendering. GA-R9 only defines readiness requirements.

## Source and behavior confirmations

- EDGE source modified: no
- LINK source modified: no
- Contracts source modified: no
- UFMS repository/source modified or accessed: no
- HMI runtime execution added: no
- HMI control added: no
- Drawing upload added: no
- Customer drawing reference added: no
- BIM runtime integration added: no
- Connector/device/runtime call added: no
- Real OPC/SNMP/Modbus/BACnet/API/SDK integration added: no
- Backend API behavior modified: no
- Frontend behavior modified: no
- UConsole behavior modified: no
- ONE Adapter introduced: no
- POST/PUT/PATCH/DELETE Airport API client methods added: no

## Validation commands

- `git status -sb`
- `git log --oneline -12`
- `git tag --points-at HEAD`
- `grep -R "ONE_AIRPORT_GA_R8_ENGINEER_COMMISSIONING_DIAGNOSTICS_READINESS_PASS" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv`
- `python3 scripts/validation/validate-one-airport-ga-r9-graphics-hmi-equipment-locator-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r8-engineer-commissioning-diagnostics-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r6-link-integration-readiness.py`
- `python3 scripts/validation/validate-one-airport-ga-r5a-local-release-freeze.py`
- `python3 scripts/validation/validate-one-airport-ga-r5-stakeholder-review-package.py`
- `python3 scripts/validation/validate-one-airport-ga-r4-uconsole-binding.py`
- `python3 scripts/validation/validate-one-airport-ga-r3-readonly-frontend-page.py`
- `python3 scripts/validation/validate-one-airport-ga-r2-readonly-api-smoke-regression.py`
- `python3 scripts/validation/validate-one-airport-ga-readonly-api-routes.py`
- `python3 scripts/validation/validate-one-package-route-enforcement.py`
- `python3 scripts/validation/validate-one-boundaries.py`
- `python3 -m json.tool AN_VANTARIS_ONE/projections/airport-graphics-hmi-equipment-locator-readiness.v1.json`
- `python3 -m json.tool AN_VANTARIS_ONE/registries/airport-graphics-hmi-equipment-locator-readiness-registry.v1.json`

## Validation results

- GA-R9 Graphics HMI equipment locator readiness validator: expected PASS
- GA-R8 engineer commissioning diagnostics readiness regression: expected PASS
- GA-R7 existing-system onboarding mapping readiness regression: expected PASS
- GA-R6 LINK integration readiness projection regression: expected PASS
- GA-R5A local release freeze regression: expected PASS
- GA-R5 stakeholder package regression: expected PASS
- GA-R4 UConsole binding regression: expected PASS
- GA-R3 frontend read-only page regression: expected PASS
- GA-R2 API smoke/contract regression: expected PASS
- GA-R1 API route regression: expected PASS
- Package route enforcement: expected PASS
- Boundary baseline: expected PASS with existing non-blocking legacy warnings
- Projection JSON validation: expected PASS
- Registry JSON validation: expected PASS

## PASS marker

`ONE_AIRPORT_GA_R9_GRAPHICS_HMI_EQUIPMENT_LOCATOR_READINESS_PASS`

## Known limitations

1. Readiness projection only.
2. No Graphics HMI runtime.
3. No equipment control.
4. No drawing upload.
5. No customer-specific drawing reference.
6. No customer-specific floor-plan rendering.
7. No BIM runtime integration.
8. No connector execution.
9. No device connection.
10. No runtime EDGE/LINK call.
11. No DB write.
12. No runtime activation.
13. No production activation.
14. No approval execution.
15. No deployment execution.
16. Existing boundary warnings remain non-blocking and unchanged in posture.

## Recommended next tasks

1. Airport GA-R10 Distributed / Remote Deployment Readiness Package
2. UMMS-R2 Work Order / Asset / PM domain alignment
3. Assets-R4 Asset/location projection refinement
4. UCDE-R4 Evidence chain alignment
5. UFMS-led shared foundation: EDGE/LINK Airport ELV Phase 1
