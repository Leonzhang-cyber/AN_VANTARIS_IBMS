# SERVER-PRECHECK-R1 Dual-server Read-only Environment Audit

PASS marker: ONE_SERVER_PRECHECK_R1_DUAL_SERVER_READONLY_AUDIT_PASS

SERVER-PRECHECK-R1 adds a VANTARIS ONE read-only dual-server deployment precheck audit for customer and engineer review.

## Server Plan

- 192.168.60.21 = APP / Web / Backend / Frontend / Console / UHMI / UCDE / UMMS / Reports / Customer Delivery / Foundation Diagnostics / Asset Context / CODE / NexusAI Preview
- 192.168.60.22 = DB only

This is not deployment. It does not connect to either server, does not connect to DB, does not install packages, and does not run migration.

## Audit Chain

Customer Delivery / Engineer Installer Preview -> Foundation Diagnostics Readiness -> APP/DB Dual-server Planning -> Server Precheck Checklist -> Deployment Blockers / Risk Boundary -> Reports / UCDE / NexusAI linkage -> Customer Handoff Readiness

## Read-only Flags

- scope: SERVER_PRECHECK_R1
- moduleId: server-precheck
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
- visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE

## API Surface

- GET /api/v1/one/server-precheck/health
- GET /api/v1/one/server-precheck/summary
- GET /api/v1/one/server-precheck/server-plan
- GET /api/v1/one/server-precheck/app-server
- GET /api/v1/one/server-precheck/db-server
- GET /api/v1/one/server-precheck/checklist
- GET /api/v1/one/server-precheck/blockers
- GET /api/v1/one/server-precheck/handoff-readiness
- GET /api/v1/one/server-precheck/guardrails

## Checklist Coverage

- server OS/version
- disk space
- CPU/RAM
- network route APP->DB
- firewall ports
- DNS/hostname
- TLS cert
- Nginx
- backend runtime
- frontend static path
- PM2/systemd strategy
- PostgreSQL version
- DB backup path
- DB restore drill
- .env secret management
- offline package integrity
- rollback plan
- log/audit retention
- monitoring
- UAT account readiness

## Blockers

- No SSH/server access performed
- No deployment performed
- No DB connection tested
- No DB migration executed
- No runtime healthcheck executed
- No backup/restore drill executed
- No UAT executed
- No production monitoring enabled
- Remote branch not aligned with local latest commits

## Handoff Readiness

- customerHandoffStatus: READINESS_PREVIEW_ONLY
- serverPrecheckStatus: NOT_EXECUTED
- deploymentStatus: NOT_EXECUTED
- dbActivationStatus: NOT_EXECUTED
- productionGaStatus: NOT_YET
- nextRecommendedStep: approved read-only server access window OR final local push/tag decision

Linked modules:

- Customer Delivery
- Foundation Diagnostics
- Reports
- Asset Context
- CODE Policy Gate
- NexusAI Branch Audit

## Guardrails

- No SSH
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

