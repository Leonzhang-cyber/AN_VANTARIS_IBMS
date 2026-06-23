# CUSTOMER-DELIVERY-GA-R1 Server Plan And Offline Handoff

PASS marker: CUSTOMER_DELIVERY_GA_R1_ENGINEER_INSTALLER_CONSOLE_READONLY_PREVIEW_PASS

## APP/non-DB Server Plan

- serverIp: 192.168.60.21.
- role: APP_NON_DB.
- plannedComponents: Frontend, Backend, UConsole, UHMI, UCDE, Customer Delivery, Reports, API, EDGE/LINK engineer diagnostics preview.
- deploymentExecuted: false.
- sshExecuted: false.

## DB-only Server Plan

- serverIp: 192.168.60.22.
- role: DB_ONLY.
- plannedComponents: PostgreSQL, DB Foundation.
- deploymentExecuted: false.
- sshExecuted: false.
- migrationExecuted: false.
- dbWrite: false.

## Offline Handoff Preview

- Offline package handoff preview: read-only.
- Engineer precheck preview: read-only.
- Verification preview: read-only.
- Rollback preview: read-only.
- Acceptance preview: read-only.

## Guardrails

- No SSH.
- No deployment executed.
- No Install.
- No Rollback.
- No DB Migration.
- No DB Write.
- No Runtime Activation.
- No Direct Device Control.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.
- No Production Activation.
- No runnable production package.
- No dist/build committed.

Future production deployment requires separate approved task.

visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE.
