# SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval

PASS marker: ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS

## Purpose

SERVER-DEPLOY-R3 records the manual execution approval layer before any real runtime installation.

R3 approves the future manual execution path for the SERVER-DEPLOY-R2 command review packet. R3 does not execute installation, connect to servers, execute SSH, store real targets, run package manager commands, deploy, migrate, back up, restore, healthcheck, smoke test, or mutate server/application/database/runtime state.

## Scope

R3 is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, local release-index documentation, and manual execution approval record only.

It records manual execution approval status, execution window, operator assignment, backup checkpoint confirmation, rollback owner confirmation, stop condition confirmation, restricted credential handling, post-install evidence expectation, and GO / HOLD / NO-GO manual execution approval rules.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command with real target.
- No automatic server connection.
- No APP server connection by this packet.
- No DB server connection by this packet.
- No real server IP / hostname / username / password in public files.
- No OS package installation by this packet.
- No runtime installation by this packet.
- No PostgreSQL installation by this packet.
- No Nginx installation by this packet.
- No Node/npm installation by this packet.
- No Python/pip installation by this packet.
- No PM2 installation by this packet.
- No deployment by this packet.
- No build execution by this packet.
- No install execution by this packet.
- No restart/reload execution by this packet.
- No DB migration by this packet.
- No DB backup execution by this packet.
- No DB restore execution by this packet.
- No DB seed execution by this packet.
- No DB user creation by this packet.
- No DB privilege mutation by this packet.
- No APP-to-DB live connection test by this packet.
- No healthcheck execution by this packet.
- No smoke test execution by this packet.
- No server mutation by this packet.
- No DB/auth/runtime mutation by this packet.
- No frontend/backend/routes/menu mutation by this packet.
- No production config mutation by this packet.
- No production credential storage in public files.

## Relationship with SERVER-DEPLOY-R1/R2 and SERVER-PRECHECK-R14F

SERVER-DEPLOY-R3 follows SERVER-DEPLOY-R1 Base Runtime Installation Plan and SERVER-DEPLOY-R2 Runtime Installation Execution Packet.

SERVER-DEPLOY-R1 runtimeInstallationPlanDecision is GO. SERVER-DEPLOY-R2 runtimeInstallationExecutionPacketDecision is GO. SERVER-PRECHECK-R14F deploymentExecutionFinalApprovalDecision is GO.

R3 is the final human approval gate before a later stage may contain manually executable server commands. R3 itself does not execute commands.

## Manual Execution Approval Model

R3 may approve future manual execution. R3 does not execute that future manual execution. R3 does not store real SSH commands. R3 does not store real server targets in public files. R3 does not store production credentials.

runtimeInstallationManualApprovalDecision: GO.

This GO means manual execution approval evidence is complete enough to hand off to SERVER-DEPLOY-R4 Runtime Installation Manual Execution Record. It does not authorize automatic execution by R3.

## Execution Window Requirements

R3 defines a restricted execution window reference, timezone, start/end time references, change freeze review, operator availability, rollback owner availability, and evidence reviewer availability.

R3 must not include live server access commands.

## Operator Assignment Requirements

R3 requires a human approver, execution coordinator, APP operator, DB operator, rollback owner, and evidence reviewer.

Identities are represented by names/roles or restricted references, not credentials.

## APP Runtime Installation Approval

R3 approves future manual installation review for Python runtime, Node.js runtime, PM2 or process manager, and Nginx runtime.

R3 does not install APP runtime packages. R3 does not start, stop, restart, or reload services. R3 does not build frontend. R3 does not run backend.

## DB Runtime Installation Approval

R3 approves future manual installation review for PostgreSQL runtime, DB tooling, and backup / restore tooling.

R3 confirms PostgreSQL as DB direction. R3 does not install PostgreSQL. R3 does not run psql. R3 does not create DB users. R3 does not grant privileges. R3 does not run migration, backup, restore, or seed.

## Offline / No-Docker Approval

Docker is not required. No-Docker path is approved for the future manual execution path. Offline mode, offline package inventory, and offline bundle integrity check are approved for the approval model.

## Pre-install Backup Checkpoint Approval

Backup is required before installation. Backup checkpoint is approved for the future execution model. Backup operator is assigned by restricted reference. R3 does not execute backup.

## Rollback Owner and Rollback Checkpoint Approval

Rollback plan is required. Rollback checkpoint is approved. Rollback owner is assigned by restricted reference. R3 does not execute rollback.

## Stop Condition Approval

Stop conditions include wrong server target, package integrity failure, missing backup checkpoint, unauthorized privilege escalation, secret leakage, unexpected mutation, missing APP or DB operator, and unavailable rollback owner.

## Restricted Credential Handling

R3 prohibits public storage of APP secrets, JWT secrets, API keys, database connection strings, DB passwords, PostgreSQL superuser credentials, APP DB user credentials, Flask secret keys, session secrets, private keys, SSH keys, server passwords, real SSH targets, internal hostnames, private IPs, usernames, emails, customer-specific server names, sensitive production paths, and production environment file content.

Secrets can only be represented by restricted evidence references. Public release index must not include raw secrets, production environment file content, real SSH targets, or production credentials.

## Post-install Evidence Requirements

Future post-install evidence must include runtime presence evidence, package version evidence, service status evidence, backup checkpoint evidence, rollback checkpoint evidence, operator execution record, redacted public evidence, and restricted raw evidence references if required.

R3 does not collect live evidence.

## Next-stage Execution Boundary

Recommended next stage: SERVER-DEPLOY-R4 Runtime Installation Manual Execution Record.

R4 must separately record any future manual execution. R3 does not grant automatic execution rights.

## GO / HOLD / NO-GO Manual Approval Rules

HOLD applies if R2 runtime installation execution packet is missing, R2 decision is not GO, execution window is missing, human approver is missing, APP operator is missing, DB operator is missing, rollback owner is missing, backup checkpoint is not approved, rollback checkpoint is not approved, stop conditions are not approved, offline/no-Docker approval is incomplete, or secret handling is unresolved.

GO applies if R2 runtime installation execution packet exists, R2 decision is GO, execution window is defined, human approver is assigned, execution coordinator is assigned, APP operator is assigned, DB operator is assigned, rollback owner is assigned, evidence reviewer is assigned, APP runtime manual approval is reviewed, DB runtime manual approval is reviewed, offline/no-Docker approval is reviewed, backup checkpoint is approved, rollback checkpoint is approved, stop conditions are approved, restricted secret handling passed, no installation or mutation occurred in R3, reviewer accepted, and approver status is GO.

NO-GO applies if installation was performed by this packet, SSH execution was performed by this packet, APP or DB server connection was performed by this packet, real SSH target or server credential was stored in public packet, OS/runtime/PostgreSQL/Nginx/Node/Python/PM2 installation was performed by this packet, APP or DB command was executed by this packet, DB migration/backup/restore/seed/user/privilege mutation was performed by this packet, build/install/restart/reload was performed by this packet, live APP-to-DB connection test was performed by this packet, healthcheck/smoke was executed by this packet, server mutation was detected, auth/runtime/frontend/backend/route/menu mutation was detected, production config mutation was detected, production secret leakage was detected, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R1/R2/R14F references, R1/R2 GO decisions, manual approval fields, false execution/mutation fields, execution window, operator assignment, APP/DB approvals, PostgreSQL direction, offline/no-Docker approval, backup checkpoint, rollback checkpoint, stop conditions, post-install evidence approval, secret handling, runtimeInstallationManualApprovalDecision, source markers, absence of real target executable operation steps, and PASS marker presence.

## Boundary Statement

SERVER-DEPLOY-R3 records manual execution approval only.

It does not execute SSH, create SSH automation, store SSH commands with real targets, automatically connect to servers, connect to APP or DB servers, execute APP/DB/OS commands, install packages or runtimes, deploy, build, install, restart, reload, run DB migration/backup/restore/seed/user/privilege changes, test APP-to-DB live connectivity, execute healthchecks or smoke tests, mutate servers, DB/auth/runtime/frontend/backend/routes/menu implementation/production config, store production credentials in public files, or perform runtime installation by this packet.

## PASS Marker

ONE_SERVER_DEPLOY_R3_RUNTIME_INSTALLATION_MANUAL_EXECUTION_APPROVAL_PASS
