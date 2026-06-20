# ONE-AIRPORT-GA-R7 Existing System Onboarding + Mapping Readiness Report

## Baseline HEAD and tag

- Baseline HEAD: `dbf88514cb48b2994dd69276065d0b3316f08474`
- Baseline tag: `airport-ga-readonly-stakeholder-review-local-freeze-20260621`
- GA-R6 dependency: `ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS`
- Branch state before GA-R7: `main...origin/main [ahead 1]`

## Changed files

- `AN_VANTARIS_ONE/projections/airport-existing-system-onboarding-mapping-readiness.v1.json`
- `AN_VANTARIS_ONE/registries/airport-existing-system-onboarding-mapping-readiness-registry.v1.json`
- `ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_REPORT.md`
- `scripts/validation/validate-one-airport-ga-r7-existing-system-onboarding-mapping-readiness.py`

## Projection summary

GA-R7 adds a VANTARIS ONE-side, read-only Airport existing-system onboarding and mapping readiness projection. It describes future onboarding catalogs, mapping groups, tag normalization requirements, engineer review packet requirements, and EDGE/LINK shared foundation gaps.

GA-R7 does not implement real onboarding execution, real connector runtime, device access, EDGE/LINK runtime calls, production activation, or workflow execution.

## Existing system catalog summary

The projection covers Bosch CCTV, Bosch ACS-SMS, PA System, Radio System, Tonna IPTV, Mobatime Clock System, NEC IPBX, Armanno Toll, BMS, EMS, MMS, e-Inspection, iFeedback, and Security System.

Each catalog entry records likely integration methods, likely data objects, mapping needs, EDGE connector needs, LINK envelope needs, read-only GA status, and future ownership.

## Integration method catalog summary

The projection catalogs OPC UA, OPC TCP/IP, SNMP, Modbus TCP, BACnet/IP, REST API, SDK, CSV import, Excel import, File export, Scheduled export, and Webhook / event push future.

Each method is catalog-only in GA-R7 and records direction, future read-only support, credential/network/runtime needs, mapping, normalization, evidence, and ownership.

## Mapping readiness model summary

GA-R7 defines readiness groups for source system, connector, device, point, tag, asset reference, location reference, alarm severity, fault candidate, work-order trigger, evidence reference, and graphics HMI locator mapping.

These groups remain requirements only. Future execution belongs to EDGE/LINK shared foundation and business-context resolution belongs to VANTARIS ONE / Airport / UMMS / UCDE as appropriate.

## Tag mapping requirements summary

Future tag mapping requires raw and normalized tag identity, source system, connector, device, point, asset, location, discipline, signal, unit, quality, alarm, fault candidate, work-order trigger, and HMI symbol references.

Validation requirements include duplicate tag detection, conflict detection, missing asset/location reference detection, unit normalization, timezone normalization, quality flag normalization, and severity normalization.

## Onboarding review packet requirements

Future engineer review packets must include packet identity, source-system profile, connector profile, mapping draft, tag normalization preview, sample payload preview, alarm mapping preview, asset/location mapping preview, work-order trigger preview, HMI locator preview, risk flags, missing fields, and engineer review status.

`activationAllowed` remains false in GA-R7.

## Customer core function mapping impact

GA-R7 maps onboarding readiness to work orders, asset registry, preventive maintenance, spare parts, vendor/contract management, graphics HMI equipment location, existing-system onboarding, engineer commissioning diagnostics, remote overseas deployment, and distributed independent installation.

The projection classifies each customer function by required onboarding inputs, mapping groups, EDGE capabilities, LINK objects, ONE projections, UMMS capability, readiness status, and future phase.

## EDGE/LINK shared foundation interface requirements

EDGE future requirements include Airport ELV connector matrix, onboarding profile, tag import parser, OPC/BACnet/SNMP snapshot imports, CSV/Excel import connector, tag validation, normalization preview, sample payload preview, engineer commissioning CLI, offline/remote deployment package, hardware-key/site-binding status, and HMI locator data foundation.

LINK future requirements include source-system health, delivery readiness, canonical delivery envelope, work-order trigger, asset/location reference, audit/evidence chain, mapping profile, deployment package status, remote support bundle, and distributed topology contracts.

## Source and behavior confirmations

- EDGE source modified: no
- LINK source modified: no
- Contracts source modified: no
- UFMS repository/source modified or accessed: no
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
- `grep -R "ONE_AIRPORT_GA_R6_LINK_INTEGRATION_READINESS_PROJECTION_PASS" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv`
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
- `python3 -m json.tool AN_VANTARIS_ONE/projections/airport-existing-system-onboarding-mapping-readiness.v1.json`
- `python3 -m json.tool AN_VANTARIS_ONE/registries/airport-existing-system-onboarding-mapping-readiness-registry.v1.json`

## Validation results

- GA-R7 existing-system onboarding mapping readiness validator: expected PASS
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

`ONE_AIRPORT_GA_R7_EXISTING_SYSTEM_ONBOARDING_MAPPING_READINESS_PASS`

## Known limitations

1. Readiness projection only.
2. No production onboarding.
3. No runtime activation.
4. No connector execution.
5. No device connection.
6. No runtime EDGE/LINK call.
7. No DB write.
8. No approval execution.
9. No deployment execution.
10. No remote command execution.
11. No work-order lifecycle execution.
12. No asset lifecycle write.
13. Existing boundary warnings remain non-blocking and unchanged in posture.

## Recommended next tasks

1. Airport GA-R8 Engineer Commissioning Diagnostics Readiness
2. Airport GA-R9 Graphics HMI Equipment Locator Readiness
3. Airport GA-R10 Distributed / Remote Deployment Readiness Package
4. UMMS-R2 Work Order / Asset / PM domain alignment
5. UFMS-led shared foundation: EDGE/LINK Airport ELV Phase 1
