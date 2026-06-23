# SERVER-PRECHECK-R2 Approved Read-only Server Access Window Plan

PASS marker: ONE_SERVER_PRECHECK_R2_READONLY_ACCESS_WINDOW_PLAN_PASS

SERVER-PRECHECK-R2 defines an approved read-only server access window plan before any actual observation of the APP server 192.168.60.21 and DB-only server 192.168.60.22.

This is not actual SSH, not deployment, not install, not DB connection, not migration, not runtime healthcheck, and not production activation.

## Scope

- scope: SERVER_PRECHECK_R2
- moduleId: server-access-window-plan
- visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE
- access window: PLANNING_ONLY
- planning-only
- not executed in R2

## Audit Chain

SERVER-PRECHECK-R1 Dual-server Read-only Environment Audit -> Approved Read-only Server Access Window Plan -> Customer / Engineer / Security Approval Boundary -> Allowed Read-only Command Catalog -> Evidence Capture Plan -> Stop / Abort Conditions -> SERVER-PRECHECK-R3 actual read-only access candidate

## Read-only Flags

- readOnly: true
- sshExecuted: false
- deploymentExecuted: false
- installExecuted: false
- dbConnectionExecuted: false
- dbMigrationExecuted: false
- dbWriteEnabled: false
- healthcheckRuntimeExecuted: false
- nginxSetupExecuted: false
- pm2SetupExecuted: false
- systemdSetupExecuted: false
- edgeCommandExecution: false
- linkCommandExecution: false
- deviceControlEnabled: false
- productionActivation: false

## API Surface

- GET /api/v1/one/server-access-plan/health
- GET /api/v1/one/server-access-plan/summary
- GET /api/v1/one/server-access-plan/access-window
- GET /api/v1/one/server-access-plan/approval-boundary
- GET /api/v1/one/server-access-plan/allowed-readonly-commands
- GET /api/v1/one/server-access-plan/evidence-capture
- GET /api/v1/one/server-access-plan/stop-conditions
- GET /api/v1/one/server-access-plan/r3-readiness
- GET /api/v1/one/server-access-plan/guardrails

## Access Window

- proposedWindowStatus: NOT_SCHEDULED
- read-only terminal access only after explicit approval
- no sudo unless separately approved
- no write command
- no package install
- no service restart
- planned read-only commands, not executed in R2

## Approval Boundary

- Customer permission to access 192.168.60.21
- Customer permission to access 192.168.60.22
- SSH account confirmation
- Read-only command list approval
- No DB mutation approval boundary
- Evidence capture approval
- Stop condition acknowledgement

## Allowed Read-only Commands

APP server examples: hostname, date, whoami, uname -a, df -h, free -h, uptime, ip addr show, ss -tulpen, nginx -v, node -v, npm -v, python3 --version, pm2 list, systemctl status nginx, systemctl status vantaris-app.

DB server examples: hostname, date, whoami, uname -a, df -h, free -h, uptime, ip addr show, ss -tulpen, psql --version, systemctl status postgresql, pg_isready.

These are allowed read-only commands as plan text only, not executed in R2.

## Evidence Capture

- evidencePlanStatus: PLANNED_NOT_CAPTURED
- access approval record
- command transcript
- server identity output
- OS/resource output
- port/listener output
- package version output
- DB readiness output
- blocker log
- R3 readiness decision
- UCDE evidence write: false
- Reports export: false

## Stop Conditions

- Login lands on unexpected server
- Account has unexpected sudo/root
- Customer says stop
- Output shows production workload risk
- DB mutation would be required
- Service restart would be required
- Credentials/secrets exposure detected
- Any command not on approved list is needed
- Network instability
- Security owner withdraws approval

## R3 Readiness

- r3Candidate: SERVER-PRECHECK-R3 Actual Approved Read-only Server Observation
- readyForR3: false
- prerequisites: written approval, access window scheduled, accounts verified, command list approved, evidence folder prepared, stop conditions accepted
- blockers: No access window scheduled, No approval captured, No credentials validated, No evidence capture target confirmed

## Guardrails

- No SSH in R2
- No deployment
- No install
- No DB connection
- No DB migration
- No DB write
- No runtime healthcheck
- No Nginx/PM2/systemd setup
- No EDGE/LINK command
- No device control
- No production activation

