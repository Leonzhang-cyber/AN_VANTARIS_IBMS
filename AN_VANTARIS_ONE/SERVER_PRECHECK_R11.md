# SERVER-PRECHECK-R11 DB Server Deployment Preparation Pack

PASS marker: ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS

## Purpose

SERVER-PRECHECK-R11 defines the DB server deployment preparation package for VANTARIS ONE / IBMS after the R10 deployment readiness gate.

R11 defines preparation rules, evidence model, restricted credential handling, validation gate, and GO / HOLD / NO-GO criteria before DB deployment can be considered. It does not execute deployment.

## Scope

R11 is documentation, registry JSON, evidence JSON, validation JSON, validator, final verification note, and release-index documentation only.

It defines PostgreSQL direction confirmation, target DB server references, migration preparation, backup preparation, rollback preparation, seed preparation, APP-to-DB connection preparation, DB credential handling, restricted evidence handling, reviewer model, approver model, and preparation decision rules.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command.
- No executable shell script.
- No DB server connection.
- No PostgreSQL command execution.
- No deployment.
- No install.
- No DB migration.
- No DB backup execution.
- No DB restore execution.
- No DB seed execution.
- No DB user creation.
- No DB privilege mutation.
- No APP server mutation.
- No DB server mutation.
- No auth mutation.
- No runtime mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No production config mutation.
- No production credential storage in public files.
- No actual DB deployment execution by this packet.

## Relationship with R1-R10

- R1: Dual-server read-only audit.
- R2: Read-only access window plan.
- R3: Actual read-only observation plan.
- R4: Read-only SSH execution approval packet.
- R5: Actual read-only observation entry gate.
- R6: Manual read-only observation command pack.
- R7: Human approval record and observation window lock.
- R8: Manual observation evidence packet.
- R9: Actual read-only observation evidence record.
- R10: Deployment readiness gate.
- R11: DB server deployment preparation pack.

R11 follows R10 and prepares DB deployment, but does not execute deployment.

## DB Deployment Preparation Model

The R11 evidence pack must preserve these core fields:

```json
{
  "packId": "server-precheck-r11-db-server-deployment-preparation-pack",
  "stage": "SERVER-PRECHECK-R11",
  "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
  "approvalReference": "SERVER-PRECHECK-R7",
  "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
  "dbDeploymentPerformedByThisPacket": false,
  "sshExecutedByThisPacket": false,
  "dbServerConnectionPerformed": false,
  "postgresCommandExecuted": false,
  "dbMigrationPerformed": false,
  "dbBackupPerformed": false,
  "dbRestorePerformed": false,
  "dbSeedPerformed": false,
  "dbUserCreated": false,
  "dbPrivilegeMutationPerformed": false,
  "serverMutationPerformed": false,
  "authMutationPerformed": false,
  "runtimeMutationPerformed": false,
  "frontendBackendMutationPerformed": false,
  "productionConfigMutationPerformed": false,
  "postgresqlDirectionConfirmed": true,
  "targetDbServer": {
    "serverReference": "",
    "environmentName": "",
    "networkZoneReference": "",
    "dbEngine": "PostgreSQL",
    "dbEngineVersionReference": "",
    "deploymentPathReference": "",
    "accessBoundaryReference": ""
  },
  "migrationPreparation": {
    "schemaSourceReviewed": false,
    "migrationInventoryReviewed": false,
    "migrationOrderReviewed": false,
    "migrationDryRunRequired": true,
    "migrationExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "backupPreparation": {
    "backupRequiredBeforeMigration": true,
    "backupPlanReviewed": false,
    "backupLocationReference": "",
    "backupRetentionReviewed": false,
    "backupExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "rollbackPreparation": {
    "rollbackPlanRequired": true,
    "rollbackPlanReviewed": false,
    "restoreProcedureReviewed": false,
    "restoreExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "seedPreparation": {
    "seedRequired": false,
    "seedInventoryReviewed": false,
    "seedDataSensitivityReviewed": false,
    "seedExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "appDbConnectionPreparation": {
    "appToDbConnectionPlanReviewed": false,
    "databaseUrlStoredInPublicPacket": false,
    "restrictedCredentialReferenceOnly": true,
    "networkConnectivityPlanReviewed": false,
    "leastPrivilegePlanReviewed": false,
    "readinessStatus": "HOLD"
  },
  "secretHandling": {
    "productionDbPasswordStoredInPublicPacket": false,
    "databaseUrlStoredInPublicPacket": false,
    "credentialRotationPlanReviewed": false,
    "restrictedSecretReferenceOnly": true,
    "readinessStatus": "HOLD"
  },
  "reviewer": {
    "name": "",
    "role": "",
    "reviewStatus": "PENDING"
  },
  "approver": {
    "name": "",
    "role": "",
    "approvalStatus": "HOLD"
  },
  "preparationDecision": "HOLD",
  "notes": ""
}
```

Additional traceability fields may be added, but the core boundary fields must not be removed.

## PostgreSQL Direction Confirmation

VANTARIS ONE / IBMS DB direction is PostgreSQL.

R11 must not reintroduce MySQL as the target architecture.

MySQL checks, MySQL smoke tests, and MySQL deployment assumptions are out of scope.

## DB Server Target Reference Requirements

The target DB server reference must document environment name, network zone reference, PostgreSQL engine direction, DB engine version reference, deployment path reference, and access boundary reference.

R11 does not connect to the DB server and does not verify the target by executing commands.

## Migration Preparation Requirements

R11 defines, but does not execute:

- schema source review
- migration inventory review
- migration ordering review
- migration dry-run requirement
- migration rollback consideration
- migration operator approval requirement
- migration evidence reference

R11 does not execute migration.

R11 does not create migration files.

R11 does not modify Prisma / SQLAlchemy / DB schema files.

R11 does not run migration commands.

## Backup Preparation Requirements

R11 defines, but does not execute:

- backup required before DB deployment
- backup storage location reference
- backup retention expectation
- backup operator assignment
- backup evidence record requirement
- backup verification requirement

R11 does not execute backup.

R11 does not execute restore.

R11 does not create backup scripts.

R11 does not store production backup files.

## Rollback Preparation Requirements

R11 defines rollback plan review before DB deployment. Restore procedure must be reviewed, rollback decision owner must be identified, rollback evidence must be captured, and rollback execution remains out of scope for R11.

## Seed Preparation Requirements

R11 defines whether seed is required, seed inventory review, seed sensitivity review, seed execution approval requirement, and seed rollback consideration.

R11 does not execute seed.

R11 does not create seed data.

R11 does not modify production seed content.

## APP-to-DB Connection Preparation Requirements

R11 defines APP-to-DB connection plan review, DB network boundary review, DB user privilege review, least privilege requirement, DATABASE_URL restricted handling, and connection evidence reference.

Production DATABASE_URL must not be stored in public docs or JSON.

Production DB credentials must not be committed.

Connection strings must be referenced only through restricted evidence references.

## DB Credential and Secret Handling Requirements

R11 prohibits public storage of:

- DB password
- DATABASE_URL
- PostgreSQL superuser credential
- APP DB user credential
- API key
- JWT secret
- Private key
- SSH key
- Internal hostname
- Private IP
- Username
- Email
- Customer-specific server name
- Sensitive production path

Secrets can only be represented by restricted evidence references.

Public release index must not include raw secrets or production .env content.

## Restricted Evidence Requirements

Restricted evidence references may identify where approved credential, connection, backup, rollback, or operator evidence is controlled outside the public release packet.

Restricted evidence references must not include raw secret values, production .env content, DB passwords, DATABASE_URL values, private keys, or customer-sensitive host details in public docs or JSON.

## GO / HOLD / NO-GO DB Preparation Rules

HOLD applies if the R10 deployment readiness gate is missing, R9 observation evidence is missing, target DB server reference is missing, PostgreSQL direction is not confirmed, migration preparation is incomplete, backup preparation is incomplete, rollback preparation is incomplete, APP-to-DB connection plan is incomplete, secret handling is unresolved, reviewer is missing, or approver is missing.

GO applies only if the R10 deployment readiness gate exists, R9 observation evidence exists, target DB server reference is documented, PostgreSQL direction is confirmed, migration preparation is reviewed, backup preparation is reviewed, rollback preparation is reviewed, APP-to-DB connection plan is reviewed, restricted credential handling is reviewed, no DB deployment or mutation occurred in R11, reviewer accepted, and approver status is GO.

NO-GO applies if DB deployment was performed by this packet, SSH execution was performed by this packet, DB server connection was performed by this packet, PostgreSQL command was executed by this packet, DB migration/backup/restore/seed was executed by this packet, DB user/privilege mutation occurred, server mutation is detected, auth/runtime/frontend/backend mutation is detected, production secret leakage is detected, R10 evidence chain is rejected, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R10/R7/R9 references, all false execution and mutation flags, PostgreSQL direction confirmation, migration/backup/rollback/seed/connection/secret flags, preparationDecision model, source markers, forbidden executable server or DB operation blocks, and the PASS marker.

## Boundary Statement

SERVER-PRECHECK-R11 records a DB server deployment preparation pack only.

It does not execute SSH, does not create SSH automation, does not include SSH connection commands, does not create executable shell scripts, does not connect to the DB server, does not execute PostgreSQL commands, does not deploy, does not install, does not run migration, backup, restore, or seed, does not create DB users, does not mutate DB privileges, does not mutate APP server, DB server, auth, runtime, frontend, backend, routes, production config, secrets, or server state, and does not perform actual DB deployment by this packet.

## PASS Marker

ONE_SERVER_PRECHECK_R11_DB_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS
