# SERVER-DEPLOY-R1 Base Runtime Installation Plan

PASS marker: ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS

## Purpose

SERVER-DEPLOY-R1 creates the base runtime installation plan for the APP Server and DB Server after SERVER-PRECHECK-R14F recorded deploymentExecutionFinalApprovalDecision as GO.

R1 is still a plan. It does not install anything, connect to servers, execute SSH, run package manager commands, deploy, migrate, back up, restore, healthcheck, smoke test, or mutate server/application/database/runtime state.

## Scope

R1 is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, and local release-index documentation only.

It defines the installation plan, approval model, runtime inventory, offline/no-Docker path, backup/rollback prerequisites, stop conditions, validation model, and GO / HOLD / NO-GO planning rules before actual runtime installation can begin in a later packet.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command.
- No executable shell script.
- No APP server connection.
- No DB server connection.
- No OS package installation.
- No runtime installation.
- No PostgreSQL installation.
- No Nginx installation.
- No Node/npm installation.
- No Python/pip installation.
- No PM2 installation.
- No deployment.
- No build execution.
- No install execution.
- No restart/reload execution.
- No DB migration.
- No DB backup execution.
- No DB restore execution.
- No DB seed execution.
- No DB user creation.
- No DB privilege mutation.
- No APP-to-DB live connection test.
- No healthcheck execution.
- No smoke test execution.
- No server mutation.
- No DB/auth/runtime mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No menu implementation mutation.
- No production config mutation.
- No production credential storage in public files.
- No actual runtime installation by this packet.

## Relationship with SERVER-PRECHECK-R14F

SERVER-DEPLOY-R1 follows SERVER-PRECHECK-R14F Deployment Execution Approval Final Verification.

R14F dependency status is GO. R1 may therefore define the base runtime installation plan, but R1 does not execute installation.

R1 also references MENU-GA-R1/R2, SERVER-PRECHECK-R10, SERVER-PRECHECK-R11, SERVER-PRECHECK-R12, and SERVER-PRECHECK-R13F as upstream readiness and Console GA baselines.

## Base Runtime Installation Plan Model

The base runtime installation plan covers target server inventory requirements, APP runtime requirements, DB runtime requirements, offline/no-Docker installation path, runtime package source requirements, backup/rollback/stop conditions, restricted evidence handling, operator assignment, approval window, and next-stage execution boundary.

runtimeInstallationPlanDecision: GO.

This GO means the plan is complete enough to hand off to SERVER-DEPLOY-R2 Runtime Installation Execution Packet design. It does not authorize execution by this packet.

## Target Server Inventory Requirements

APP Server inventory must define a restricted server reference, environment name, network zone reference, OS family/version reference, CPU / memory / disk review, installation user reference, and installation window reference.

DB Server inventory must define a restricted server reference, environment name, network zone reference, OS family/version reference, CPU / memory / disk review, installation user reference, and installation window reference.

R1 must not include live server commands or public raw production identifiers.

## APP Server Runtime Plan

The APP Server runtime plan defines Python runtime requirement, Node.js runtime requirement, PM2 requirement, Nginx requirement, package manager strategy, runtime version plan, online/offline installation source, install order, and rollback consideration.

R1 does not install Python. R1 does not install Node.js. R1 does not install PM2. R1 does not install Nginx. R1 does not run npm, pip, systemctl, or package manager commands.

## DB Server Runtime Plan

The DB Server runtime plan defines PostgreSQL requirement, PostgreSQL version plan, DB user/privilege planning dependency, backup tooling plan, restore tooling plan, online/offline installation source, install order, and rollback consideration.

R1 confirms PostgreSQL as the DB direction. R1 does not install PostgreSQL. R1 does not run psql. R1 does not create DB users. R1 does not grant DB privileges. R1 does not run DB migration, backup, restore, or seed.

## Offline / No-Docker Installation Path

Docker is not required for this deployment path. No-Docker deployment path is reviewed. Offline mode must be supported as a possible customer-server condition. Offline package inventory must be prepared before execution. Offline bundle integrity check must be required before execution.

R1 does not create offline bundles or install packages.

## Runtime Package Source Requirements

Runtime package sources must be reviewed before execution. Online and offline package source strategies must be documented in restricted execution evidence. Offline package inventory and integrity checks are required before R2 execution design can proceed.

## Backup / Rollback / Stop Condition Requirements

R1 defines pre-installation backup requirement, rollback plan requirement, rollback owner requirement, stop conditions requirement, and post-installation verification planning.

R1 does not execute backup, rollback, restore, healthcheck, or smoke tests.

## Credential and Restricted Evidence Requirements

R1 prohibits public storage of APP secrets, JWT secrets, API keys, database connection strings, DB passwords, PostgreSQL superuser credentials, APP DB user credentials, Flask secret keys, session secrets, private keys, SSH keys, server passwords, internal hostnames, private IPs, usernames, emails, customer-specific server names, sensitive production paths, and production environment file content.

Secrets can only be represented by restricted evidence references. Public release index must not include raw secrets or production environment file content.

## Installation Operator and Approval Window Requirements

R1 requires an installation operator, DB operator, APP operator, rollback owner, approval window, and human approver to be represented by restricted references before execution can begin in a later packet.

## Next-stage Execution Boundary

Recommended next stage: SERVER-DEPLOY-R2 Runtime Installation Execution Packet.

R2 must remain separately approved and must not infer execution authorization from R1 alone.

## GO / HOLD / NO-GO Planning Rules

HOLD applies if R14F final deployment approval is missing, R14F final decision is not GO, target APP Server inventory is incomplete, target DB Server inventory is incomplete, APP runtime plan is incomplete, DB runtime plan is incomplete, offline/no-Docker path is incomplete, backup/rollback/stop conditions are incomplete, operator/approver is missing, or secret handling is unresolved.

GO applies if R14F final deployment approval exists, R14F final decision is GO, APP Server inventory is reviewed, DB Server inventory is reviewed, APP runtime plan is reviewed, DB runtime plan is reviewed, PostgreSQL direction is confirmed, offline/no-Docker path is reviewed, backup/rollback/stop conditions are reviewed, restricted secret handling passed, operators and approver are assigned by restricted references, no installation or mutation occurred in R1, reviewer accepted, and approver status is GO.

NO-GO applies if installation was performed by this packet, SSH execution was performed by this packet, APP or DB server connection was performed by this packet, OS/runtime/PostgreSQL/Nginx/Node/Python/PM2 installation was performed by this packet, APP or DB command was executed by this packet, DB migration/backup/restore/seed/user/privilege mutation was performed by this packet, build/install/restart/reload was performed by this packet, live APP-to-DB connection test was performed by this packet, healthcheck/smoke was executed by this packet, server mutation was detected, auth/runtime/frontend/backend/route/menu mutation was detected, production config mutation was detected, production secret leakage was detected, R14F decision is not GO, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R14F reference, R14F GO decision, false execution/mutation fields, target server readiness, APP runtime plan, DB runtime plan, PostgreSQL direction, offline/no-Docker requirements, backup/rollback/stop-condition requirements, secret handling, runtimeInstallationPlanDecision, source markers, absence of executable operation steps, and PASS marker presence.

## Boundary Statement

SERVER-DEPLOY-R1 records a base runtime installation plan only.

It does not execute SSH, create SSH automation, include SSH connection commands, create executable scripts, connect to APP or DB servers, execute APP/DB/OS commands, install packages or runtimes, deploy, build, install, restart, reload, run DB migration/backup/restore/seed/user/privilege changes, test APP-to-DB live connectivity, execute healthchecks or smoke tests, mutate servers, DB/auth/runtime/frontend/backend/routes/menu implementation/production config, store production credentials in public files, or perform actual runtime installation by this packet.

## PASS Marker

ONE_SERVER_DEPLOY_R1_BASE_RUNTIME_INSTALLATION_PLAN_PASS
