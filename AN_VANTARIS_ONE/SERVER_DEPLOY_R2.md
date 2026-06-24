# SERVER-DEPLOY-R2 Runtime Installation Execution Packet

PASS marker: ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS

## Purpose

SERVER-DEPLOY-R2 creates the runtime installation execution packet and manual command review pack for future APP / DB server runtime installation.

R2 is a reviewable execution packet. It does not execute installation automatically, connect to servers, execute SSH, run package manager commands, deploy, migrate, back up, restore, healthcheck, smoke test, or mutate server/application/database/runtime state.

## Scope

R2 is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, local release-index documentation, and manual command review packet documentation only.

It defines a manual execution packet model, APP runtime installation sequence, DB runtime installation sequence, offline/no-Docker execution path, pre-install backup checkpoint, rollback checkpoint, stop conditions, operator approval, post-install evidence format, restricted credential handling, and GO / HOLD / NO-GO execution readiness rules.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command with real target.
- No automatic server connection.
- No APP server connection by this packet.
- No DB server connection by this packet.
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

## Relationship with SERVER-DEPLOY-R1 and SERVER-PRECHECK-R14F

SERVER-DEPLOY-R2 follows SERVER-DEPLOY-R1 Base Runtime Installation Plan.

SERVER-DEPLOY-R1 runtimeInstallationPlanDecision is GO.

SERVER-PRECHECK-R14F deploymentExecutionFinalApprovalDecision is GO.

R2 defines the reviewable execution packet for a later approved manual execution stage. R2 itself does not execute commands.

## Runtime Installation Execution Packet Model

R2 records a manual command review only model. Commands are templates for human review and must use placeholders such as `<APP_SERVER>`, `<DB_SERVER>`, `<INSTALL_USER>`, and `<PACKAGE_SOURCE>`.

runtimeInstallationExecutionPacketDecision: GO.

This GO means the execution packet is complete enough to hand off to SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval. It does not authorize automatic execution by R2.

## Manual Command Review Packet Rules

R2 may include command templates only if they are clearly marked as templates for human review.

- No real SSH user, host, IP, domain, password, private key, or customer server name.
- No executable script file.
- No direct copy-paste production command block with real target.
- Command templates must use placeholders.
- Commands must be stored as review templates only, not execution instructions.
- Actual execution must be deferred to a later approved stage.

Allowed placeholder examples include `<PACKAGE_MANAGER> install <RUNTIME_PACKAGE_NAME>`, `<PROCESS_MANAGER> status <SERVICE_NAME>`, and `<DB_TOOL> --version`.

## APP Server Runtime Installation Sequence

APP Server review sequence includes OS package manager review, Python runtime review, Node.js runtime review, PM2 / process manager review, Nginx runtime review, package source review, offline bundle review, rollback checkpoint, and stop condition checkpoint.

R2 does not install Python. R2 does not install Node.js. R2 does not install PM2. R2 does not install Nginx. R2 does not run npm, pip, systemctl, or package manager commands.

## DB Server Runtime Installation Sequence

DB Server review sequence includes PostgreSQL runtime review, PostgreSQL version plan review, DB tooling review, backup tooling review, restore tooling review, package source review, offline bundle review, rollback checkpoint, and stop condition checkpoint.

R2 confirms PostgreSQL as the DB direction. R2 does not install PostgreSQL. R2 does not run psql. R2 does not create DB users. R2 does not grant DB privileges. R2 does not run DB migration, backup, restore, or seed.

## Offline / No-Docker Execution Path

Docker is not required. No-Docker path remains the default deploy path. Offline mode must be supported. Offline package inventory must be reviewed before execution. Offline bundle integrity check must be planned before execution. Online package source fallback can be documented but not executed.

## Pre-install Backup Checkpoint

Backup is required before installation. Backup checkpoint must be confirmed before any future runtime installation. Backup evidence is required after execution in a later stage. R2 does not execute backup.

## Rollback Checkpoint

Rollback plan is required. Rollback owner is required. Rollback checkpoint must be confirmed before future runtime installation. R2 does not execute rollback.

## Stop Conditions

Stop conditions include wrong server target, package integrity failure, missing backup checkpoint, privilege escalation outside approval, secret exposure in output, unexpected mutation, missing APP operator, missing DB operator, missing rollback owner, or reviewer/approver rejection.

## Operator Approval Requirements

R2 requires an execution window, human approver, APP operator, DB operator, rollback owner, and manual execution confirmation before any later stage can execute commands.

## Post-install Evidence Format

Future post-install evidence must be redacted and may include package version evidence, runtime presence evidence, service status evidence, backup checkpoint evidence, rollback checkpoint evidence, operator/reviewer/approver record, and restricted raw evidence references if needed.

R2 does not collect real runtime evidence.

## Restricted Credential Handling

R2 prohibits public storage of APP secrets, JWT secrets, API keys, database connection strings, DB passwords, PostgreSQL superuser credentials, APP DB user credentials, Flask secret keys, session secrets, private keys, SSH keys, server passwords, internal hostnames, private IPs, usernames, emails, customer-specific server names, sensitive production paths, production environment file content, and real SSH command targets.

Secrets can only be represented by restricted evidence references. Public release index must not include raw secrets or production environment file content.

## Next-stage Execution Boundary

Recommended next stage: SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval.

R3 must separately approve any future manual execution. R2 does not grant automatic execution rights.

## GO / HOLD / NO-GO Execution Packet Rules

HOLD applies if R1 runtime installation plan is missing, R1 decision is not GO, APP runtime execution sequence is incomplete, DB runtime execution sequence is incomplete, offline/no-Docker execution path is incomplete, pre-install backup checkpoint is incomplete, rollback checkpoint is incomplete, stop conditions are incomplete, operator/approver is missing, or secret handling is unresolved.

GO applies if R1 runtime installation plan exists, R1 decision is GO, APP runtime execution sequence is reviewed, DB runtime execution sequence is reviewed, PostgreSQL direction is confirmed, offline/no-Docker path is reviewed, pre-install backup checkpoint is defined, rollback checkpoint is defined, stop conditions are reviewed, restricted secret handling passed, operators and approver are assigned, no installation or mutation occurred in R2, reviewer accepted, and approver status is GO.

NO-GO applies if installation was performed by this packet, SSH execution was performed by this packet, APP or DB server connection was performed by this packet, real SSH target or server credential was stored in public packet, OS/runtime/PostgreSQL/Nginx/Node/Python/PM2 installation was performed by this packet, APP or DB command was executed by this packet, DB migration/backup/restore/seed/user/privilege mutation was performed by this packet, build/install/restart/reload was performed by this packet, live APP-to-DB connection test was performed by this packet, healthcheck/smoke was executed by this packet, server mutation was detected, auth/runtime/frontend/backend/route/menu mutation was detected, production config mutation was detected, production secret leakage was detected, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R1/R14F references, R1 GO decision, manual review fields, false execution/mutation fields, command template rules, APP/DB sequence review, offline/no-Docker review, backup checkpoint, rollback checkpoint, stop conditions, post-install evidence format, secret handling, runtimeInstallationExecutionPacketDecision, source markers, absence of real target executable operation steps, and PASS marker presence.

## Boundary Statement

SERVER-DEPLOY-R2 records a runtime installation execution packet and manual command review pack only.

It does not execute SSH, create SSH automation, store SSH commands with real targets, automatically connect to servers, connect to APP or DB servers, execute APP/DB/OS commands, install packages or runtimes, deploy, build, install, restart, reload, run DB migration/backup/restore/seed/user/privilege changes, test APP-to-DB live connectivity, execute healthchecks or smoke tests, mutate servers, DB/auth/runtime/frontend/backend/routes/menu implementation/production config, store production credentials in public files, or perform runtime installation by this packet.

## PASS Marker

ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS
