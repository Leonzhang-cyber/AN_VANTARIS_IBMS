# SERVER-PRECHECK-R3 Actual Approved Read-only Server Observation Plan

PASS marker: ONE_SERVER_PRECHECK_R3_ACTUAL_READONLY_OBSERVATION_PLAN_PASS

SERVER-PRECHECK-R3 is the actual approved read-only server observation plan layer for VANTARIS ONE. It defines the final command-level plan, execution sequence, evidence package, stop conditions, approval checklist, and responsibility boundary for a future approved terminal observation window.

R3 is planned-only and not executed in R3. Actual observation requires separate approval required from the user/customer before any terminal access.

## Planning Chain

SERVER-PRECHECK-R1 Dual-server Read-only Environment Audit
-> SERVER-PRECHECK-R2 Approved Read-only Server Access Window Plan
-> SERVER-PRECHECK-R3 Actual Approved Read-only Server Observation Plan
-> future approved terminal execution only after explicit user confirmation

## Targets

- APP Server: 192.168.60.21
- DB Server: 192.168.60.22

## Boundaries

- Read-only planning only.
- No SSH.
- No deployment.
- No install.
- No DB connection.
- No DB migration.
- No DB write.
- No runtime healthcheck.
- No Nginx/PM2/systemd setup.
- No EDGE/LINK command.
- No device control.
- No production activation.
- No auth/login/JWT/RBAC mutation.
- No .env, secrets, credentials, password, token, or key material.
- No real SSH command execution script.

## Execution Sequence

The execution sequence is a planned-only timeline:

1. Confirm written approval and access window.
2. Start transcript capture.
3. Observe APP server identity and resources.
4. Observe APP server network/listeners/package versions.
5. Observe APP server service status without restart.
6. Observe DB server identity and resources.
7. Observe DB server PostgreSQL package/status only.
8. Capture blocker notes.
9. Stop if any stop condition is triggered.
10. Close evidence package.

## App Server Observation

The app server observation table lists read-only planned commands for identity, resources, listener posture, package versions, PM2 listing, and service status. Every command is marked planned-only, read-only, and not executed in R3.

## DB Server Observation

The db server observation table lists read-only planned commands for identity, resources, listener posture, PostgreSQL version, PostgreSQL status, and readiness command planning. Every command is marked planned-only, read-only, dbMutation false, and not executed in R3.

## Evidence Package

The evidence package is PLANNED_NOT_CAPTURED and includes approval record, transcript file, APP server output, DB server output, blocker list, stop condition log, and final R3 observation decision. Evidence storage is a planned local folder, not created in R3.

## Stop Conditions

Stop conditions include unexpected server identity, unexpected root/sudo requirement, unapproved command requirement, secret exposure, customer/security stop, production workload risk, service restart need, DB mutation need, network instability, unclear server role, and evidence capture failure.

## Approval Checklist

The approval checklist remains pending / not_captured / not_executed and includes customer written approval, security approval, access window scheduling, APP account verification, DB account verification, command catalog approval, evidence storage approval, stop condition acknowledgement, no sudo boundary, no DB mutation boundary, and no deployment boundary.

## Frontend

The UConsole route is `/one/server/observation-plan` with VANTARIS_LIGHT_OPERATIONS_CONSOLE styling. The page includes Summary cards, APP/DB target server cards, Execution sequence timeline, APP server planned read-only command table, DB server planned read-only command table, Evidence package plan, Stop / abort conditions, Approval checklist, Read-only guardrails panel, and Not Production GA note.

## API

All API routes are GET-only:

- `/api/v1/one/server-observation-plan/health`
- `/api/v1/one/server-observation-plan/summary`
- `/api/v1/one/server-observation-plan/execution-sequence`
- `/api/v1/one/server-observation-plan/app-server-observation`
- `/api/v1/one/server-observation-plan/db-server-observation`
- `/api/v1/one/server-observation-plan/evidence-package`
- `/api/v1/one/server-observation-plan/stop-conditions`
- `/api/v1/one/server-observation-plan/approval-checklist`
- `/api/v1/one/server-observation-plan/guardrails`
