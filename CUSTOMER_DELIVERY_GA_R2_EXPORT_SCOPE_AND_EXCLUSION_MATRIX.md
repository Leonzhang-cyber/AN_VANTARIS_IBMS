# CUSTOMER-DELIVERY-GA-R2 Export Scope And Exclusion Matrix

PASS marker: CUSTOMER_DELIVERY_GA_R2_OFFLINE_PACKAGE_READINESS_HANDOFF_DECISION_PASS

## Included Items

- docs.
- registry.
- evidence txt.
- read-only API skeleton references.
- customer handoff checklist.
- engineer runbook.
- server planning note.
- package readiness matrix.

## Referenced Items

- frontend source references.
- backend source references.
- UHMI archive.
- UCDE archive.
- Customer Delivery R1 archive.

## Excluded Items

- dist/build artifacts.
- .env/secrets.
- runtime data.
- device credentials.
- DB migrations.
- live DB connection.
- EDGE/LINK commands.
- install/uninstall/rollback execution.
- production activation.
- runnable package generation.

## Visibility Scope

Customer-visible scope: Offline Package Readiness Matrix, Customer Handoff Decision, server planning note, acceptance checklist, and exclusion matrix.

Engineer-visible scope: readiness evidence, read-only API skeleton references, engineer runbook, validation chain, and boundary status.

## Server Planning Scope

- APP / non-DB target: 192.168.60.21.
- DB-only target: 192.168.60.22.
- This is planning only.

## Forbidden Execution List

No SSH. No Install. No Rollback. No DB Migration. No DB Write. No Runtime Activation. No Direct Device Control. No EDGE Command Execution. No LINK Command Execution. No auth / login / JWT / RBAC mutation. No Production Activation. No runnable production package. No dist/build committed.

visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE.
