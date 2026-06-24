# SERVER-DEPLOY-R6 DB Deployment Preparation Execution Gate

PASS marker: ONE_SERVER_DEPLOY_R6_DB_DEPLOYMENT_PREPARATION_EXECUTION_GATE_PASS

## 1. Purpose

SERVER-DEPLOY-R6 records the DB deployment preparation execution gate after SERVER-DEPLOY-R5F. It decides whether the project is ready to proceed into a later DB deployment execution packet.

R6 follows the R5F runtimeInstallationEvidenceFinalDecision of GO and confirms that PostgreSQL runtime evidence is accepted. R6 does not execute DB deployment, connect to any server, run PostgreSQL commands, run migration, run backup, run restore, run seed, create DB users, mutate DB privileges, or perform APP-to-DB live connection testing.

## 2. Scope

R6 is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, release index documentation, and DB deployment preparation gate record only.

R6 records PostgreSQL runtime evidence dependency, DB deployment preparation readiness, DB migration execution approval readiness, pre-migration backup checkpoint readiness, rollback and restore readiness, seed readiness, DB user and privilege boundary, restricted DB credential handling, APP-to-DB connection plan review without live test, stop conditions, and GO / HOLD / NO-GO gate rules.

## 3. Non-goals

- No SSH execution by this packet.
- No SSH automation by this packet.
- No SSH connection command with real target in public files.
- No automatic server connection by this packet.
- No DB server connection by this packet.
- No APP server connection by this packet.
- No real server IP / hostname / username / password in public files.
- No production .env in public files.
- No PostgreSQL command execution by this packet.
- No psql execution by this packet.
- No DB deployment by this packet.
- No DB migration by this packet.
- No DB backup execution by this packet.
- No DB restore execution by this packet.
- No DB seed execution by this packet.
- No DB user creation by this packet.
- No DB privilege mutation by this packet.
- No DATABASE_URL stored in public files.
- No APP-to-DB live connection test by this packet.
- No healthcheck execution by this packet.
- No smoke test execution by this packet.
- No server mutation by this packet.
- No DB/auth/runtime mutation by this packet.
- No frontend/backend/routes/menu mutation by this packet.
- No production config mutation by this packet.

## 4. Relationship with SERVER-DEPLOY-R1/R2/R3/R4/R5/R5F and SERVER-PRECHECK-R14F

R6 explicitly references SERVER-PRECHECK-R14F Deployment Execution Approval Final Verification, SERVER-DEPLOY-R1 Base Runtime Installation Plan, SERVER-DEPLOY-R2 Runtime Installation Execution Packet, SERVER-DEPLOY-R3 Runtime Installation Manual Execution Approval, SERVER-DEPLOY-R4 Runtime Installation Manual Execution Record, SERVER-DEPLOY-R5 Runtime Installation Evidence Review and Gate, SERVER-DEPLOY-R5F Runtime Installation Evidence Closure Final Review, and SERVER-DEPLOY-R6 DB Deployment Preparation Execution Gate.

R6 follows R5F GO. It does not mutate earlier artifacts and creates a new DB deployment preparation gate.

## 5. DB Deployment Preparation Execution Gate Model

The R6 gate model separates preparation review from execution approval. The gate records readiness topics and stop conditions so a later SERVER-DEPLOY-R7 DB Deployment Manual Execution Approval can be created with clear inputs.

R6 current decision is HOLD because preparation items remain intentionally unresolved: migration inventory, migration order, backup checkpoint, rollback owner, restore review, seed review where applicable, least-privilege review, APP-to-DB connection plan review, reviewer assignment, approver assignment, and stop condition review.

## 6. PostgreSQL Runtime Evidence Dependency

PostgreSQL remains the DB direction.

PostgreSQL runtime evidence is accepted from SERVER-DEPLOY-R5F. DB tooling, backup tooling, and restore tooling evidence are accepted from SERVER-DEPLOY-R5F.

R6 does not install or run PostgreSQL.

## 7. DB Migration Execution Readiness

R6 requires migration inventory review, migration order review, rollback impact review, migration operator assignment, placeholder-only migration command templates if templates are used, and real DB target redaction.

R6 does not run migration. R6 does not create migration files. R6 does not modify schema files. R6 does not run psql, Prisma, Alembic, Flask-Migrate, SQLAlchemy migration, or any DB command.

## 8. Pre-migration Backup Checkpoint Readiness

Backup is required before migration. A backup checkpoint must be defined, a backup operator must be assigned, and backup evidence must be required after future execution.

R6 does not execute backup.

## 9. Rollback / Restore Readiness

Rollback plan review, restore procedure review, and rollback owner assignment are required before a future DB deployment execution packet can proceed.

R6 does not execute restore or rollback.

## 10. Seed Readiness

R6 requires the future execution packet to state whether seed is required. If seed is required, seed inventory, sensitivity review, and seed operator assignment must be completed before execution.

R6 does not run seed.

## 11. DB User / Privilege Boundary

DB user creation is excluded from R6. DB privilege mutation is excluded from R6. PostgreSQL superuser credentials must never be stored in public files.

A least-privilege DB access plan must be reviewed before later execution.

## 12. APP-to-DB Connection Plan Review

APP-to-DB connection plan must be reviewed before future execution. R6 does not perform APP-to-DB live connection testing.

DATABASE_URL must not be stored in public docs or JSON. Connection strings and DB credentials must be restricted references only.

## 13. DATABASE_URL and Credential Restricted Handling

R6 prohibits public storage of DATABASE_URL, DB password, PostgreSQL superuser credential, APP DB user credential, API key, JWT secret, private key, SSH key, server password, real DB target, internal hostname, private IP, username, customer-specific server name, sensitive production path, production .env content, and raw DB command output containing sensitive details.

Secrets can only be represented by restricted evidence references. The public release index must not include raw secrets, production .env, real DB targets, or production credentials.

## 14. Stop Conditions

Future DB deployment execution must stop if any of these conditions are detected: wrong DB target, backup checkpoint missing, migration order mismatch, secret leakage, unexpected DB mutation, unauthorized privilege escalation, or missing rollback owner.

## 15. Operator / Reviewer / Approver Requirements

Future execution requires assigned DB operator, migration operator, backup operator, rollback owner, evidence reviewer, and human approver. R6 records these requirements but does not assign production execution authority.

## 16. GO / HOLD / NO-GO DB Deployment Gate Rules

HOLD applies when R5F closure is missing, R5F decision is not GO, PostgreSQL runtime evidence is not accepted, migration inventory is incomplete, migration order is not reviewed, backup checkpoint is missing, rollback and restore readiness are incomplete, seed readiness is unresolved where seed is required, least-privilege plan is incomplete, APP-to-DB connection plan is incomplete, operator/reviewer/approver is missing, stop conditions are not reviewed, or secret handling is unresolved.

GO applies only when R5F closure exists, R5F decision is GO, PostgreSQL runtime evidence is accepted, DB tooling / backup tooling / restore tooling evidence is accepted, migration inventory and order are reviewed, rollback impact is reviewed, backup checkpoint is defined, rollback and restore readiness are reviewed, seed readiness is reviewed or marked not required, least-privilege plan is reviewed, APP-to-DB connection plan is reviewed without live test, restricted credential handling passes, stop conditions are reviewed, operators/reviewer/approver are assigned, no DB deployment or mutation occurred in R6, reviewer accepted, and approver status is GO.

NO-GO applies if DB deployment was performed by this packet, SSH execution was performed by this packet, DB server connection was performed by this packet, real DB target or DB credential was stored in a public packet, PostgreSQL command was executed by this packet, DB migration/backup/restore/seed was executed by this packet, DB user creation or privilege mutation occurred, APP-to-DB live connection test was performed by this packet, server mutation was detected, DB/auth/runtime/frontend/backend/route/menu mutation was detected, production config mutation was detected, production secret leakage was detected, R5F evidence was rejected, reviewer rejected, or approver status is NO-GO.

## 17. Validator Requirements

The validator checks that R6 documents, registry JSON, evidence JSON, validation JSON, final verification JSON, release index entry, and validator exist; source-stage references are correct; R5F dependency is GO; PostgreSQL runtime evidence is accepted; all execution, connection, command, credential, mutation, and production-config flags remain false; restricted credential handling is true; stop condition requirements are recorded; the R6 gate decision is one of HOLD, GO, or NO-GO; source markers exist; no public real target or credential patterns are present; and no executable server, DB, APP, frontend, backend, Nginx, PM2, OS package, or runtime operation steps are present.

## 18. Boundary Statement

SERVER-DEPLOY-R6 is a DB deployment preparation execution gate only. It does not execute SSH, automate SSH, store real connection targets, connect to servers, connect to DB, connect to APP, execute PostgreSQL commands, run psql, deploy DB, migrate DB, execute backup, execute restore, execute seed, create DB users, mutate DB privileges, store DATABASE_URL, perform APP-to-DB live connection test, run healthcheck or smoke test, mutate servers, mutate DB/auth/runtime, mutate frontend/backend/routes/menu, or mutate production config.

## 19. PASS Marker

ONE_SERVER_DEPLOY_R6_DB_DEPLOYMENT_PREPARATION_EXECUTION_GATE_PASS
