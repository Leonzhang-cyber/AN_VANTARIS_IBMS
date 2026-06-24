# SERVER-DEPLOY-R4 Runtime Installation Manual Execution Record

PASS marker: ONE_SERVER_DEPLOY_R4_RUNTIME_INSTALLATION_MANUAL_EXECUTION_RECORD_PASS

## Purpose

SERVER-DEPLOY-R4 defines the manual execution record model for runtime installation results after a human operator manually executes the approved runtime installation outside this repository.

R4 records the evidence structure and result decision model. R4 does not execute installation, connect to servers, execute SSH, store real targets, run package manager commands, deploy, migrate, back up, restore, healthcheck, smoke test, or mutate server/application/database/runtime state.

## Scope

R4 is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, local release-index documentation, and manual execution result record documentation only.

It defines manual execution session record, APP runtime installation result record, DB runtime installation result record, runtime presence evidence format, backup checkpoint evidence format, rollback checkpoint evidence format, stop condition outcome record, redacted evidence rules, restricted raw evidence reference rules, operator / reviewer / approver record, and GO / HOLD / NO-GO runtime installation result rules.

## Non-goals

- No SSH execution by this packet.
- No SSH automation by this packet.
- No SSH connection command with real target in public files.
- No automatic server connection by this packet.
- No APP server connection by this packet.
- No DB server connection by this packet.
- No real server IP / hostname / username / password in public files.
- No production environment file content in public files.
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

## Relationship with SERVER-DEPLOY-R1/R2/R3 and SERVER-PRECHECK-R14F

SERVER-DEPLOY-R4 follows SERVER-DEPLOY-R1 Base Runtime Installation Plan, SERVER-DEPLOY-R2 Runtime Installation Execution Packet, and SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval.

SERVER-DEPLOY-R1 runtimeInstallationPlanDecision is GO. SERVER-DEPLOY-R2 runtimeInstallationExecutionPacketDecision is GO. SERVER-DEPLOY-R3 runtimeInstallationManualApprovalDecision is GO. SERVER-PRECHECK-R14F deploymentExecutionFinalApprovalDecision is GO.

R4 records execution results, but it must not perform execution itself.

## Manual Execution Record Model

R4 records what happened after a human operator manually executed the approved runtime installation outside this repository.

This R4 packet defines the record model only. Because no external execution evidence is included in this packet, runtimeInstallationExecutionRecordDecision is HOLD.

## Execution Session Record

The execution session record defines execution session id, execution status, execution window reference, started/ended time references, within-approved-window status, and manual operator execution outside repository confirmation.

Allowed execution status values are NOT_RECORDED, COMPLETED, PARTIAL, ABORTED, FAILED, and REJECTED.

## APP Runtime Installation Result Record

The APP runtime installation result record defines Python runtime result, Node.js runtime result, PM2 / process manager runtime result, Nginx runtime result, APP runtime overall result, redacted evidence reference, and restricted raw evidence reference.

R4 must not collect real APP server evidence directly.

## DB Runtime Installation Result Record

The DB runtime installation result record defines PostgreSQL runtime result, DB tooling result, backup tooling result, restore tooling result, DB runtime overall result, redacted evidence reference, and restricted raw evidence reference.

R4 confirms PostgreSQL direction. R4 must not collect real DB server evidence directly.

## Runtime Presence Evidence Format

Runtime presence evidence covers Python, Node, PM2, Nginx, and PostgreSQL presence evidence.

Raw evidence must not be stored in the public packet. Evidence must be redacted before public release. Restricted raw evidence may only be referenced.

## Backup Checkpoint Evidence Format

Backup checkpoint evidence is required before final GO. Backup raw evidence must not be stored in the public packet. Restricted raw evidence may only be referenced.

R4 does not execute backup.

## Rollback Checkpoint Evidence Format

Rollback checkpoint evidence and rollback owner record are required before final GO. Rollback raw evidence must not be stored in the public packet. Restricted raw evidence may only be referenced.

R4 does not execute rollback.

## Stop Condition Outcome Record

R4 records whether stop conditions occurred: wrong server target, package integrity failure, backup checkpoint missing, unauthorized privilege escalation, secret leakage, unexpected mutation, operator missing, or rollback owner unavailable.

If any critical stop condition is detected, final decision must be HOLD or NO-GO.

## Redacted Evidence Requirements

Public evidence must be redacted and must contain no secrets, no real server targets, no raw command output with sensitive details, no internal hostnames, no private IPs, no usernames, no emails, no customer-specific server names, and no sensitive production paths.

## Restricted Raw Evidence Reference Requirements

Restricted raw evidence may be referenced only through restricted evidence reference identifiers. Public release index must not include raw secrets, production environment file content, real SSH targets, production credentials, or raw command output containing sensitive details.

## Operator / Reviewer / Approver Requirements

R4 requires execution coordinator record, APP operator record, DB operator record, backup operator record, rollback owner record, evidence reviewer record, reviewer status, and approver status before final GO can be considered.

## GO / HOLD / NO-GO Runtime Installation Result Rules

HOLD applies if R3 manual approval is missing, R3 decision is not GO, execution session is not recorded, APP runtime result is incomplete, DB runtime result is incomplete, runtime presence evidence is incomplete, backup checkpoint evidence is incomplete, rollback checkpoint evidence is incomplete, operator record is incomplete, post-execution evidence review is incomplete, reviewer is missing, or approver is missing.

GO applies if R3 manual approval exists, R3 decision is GO, execution session is recorded, execution occurred within approved window, APP runtime installation result is PASS or WARN with accepted rationale, DB runtime installation result is PASS or WARN with accepted rationale, runtime presence evidence is recorded and redacted, backup checkpoint evidence is recorded and redacted, rollback checkpoint evidence is recorded and redacted, no critical stop condition occurred, restricted secret handling passed, operator record completed, post-execution evidence reviewed, no public secret leakage occurred, reviewer accepted, and approver status is GO.

NO-GO applies if SSH/server connection/installation was performed by this packet instead of manual external execution, real SSH target or server credential was stored in public packet, APP runtime installation result is FAIL, DB runtime installation result is FAIL, backup checkpoint is missing, rollback owner is unavailable, wrong server target is detected, package integrity failure is detected, unauthorized privilege escalation is detected, secret leakage is detected, unexpected mutation is detected, production secret leaked into public packet, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R1/R2/R3/R14F references, GO dependency decisions, manual execution record only, false execution/mutation fields, execution session model, DB PostgreSQL direction, redacted evidence rules, backup/rollback evidence rules, stop condition flags, secret handling, post-execution evidence review, runtimeInstallationExecutionRecordDecision, source markers, absence of real target executable operation steps, and PASS marker presence.

## Boundary Statement

SERVER-DEPLOY-R4 records a runtime installation manual execution result model only.

It does not execute SSH, create SSH automation, store SSH commands with real targets, automatically connect to servers, connect to APP or DB servers, execute APP/DB/OS commands, install packages or runtimes, deploy, build, install, restart, reload, run DB migration/backup/restore/seed/user/privilege changes, test APP-to-DB live connectivity, execute healthchecks or smoke tests, mutate servers, DB/auth/runtime/frontend/backend/routes/menu implementation/production config, store production credentials in public files, or perform runtime installation by this packet.

## PASS Marker

ONE_SERVER_DEPLOY_R4_RUNTIME_INSTALLATION_MANUAL_EXECUTION_RECORD_PASS
