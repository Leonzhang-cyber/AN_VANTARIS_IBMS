# SERVER-PRECHECK-R12 APP Server Deployment Preparation Pack

PASS marker: ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS

## Purpose

SERVER-PRECHECK-R12 defines the APP server deployment preparation package for VANTARIS ONE / IBMS after the R11 DB server deployment preparation pack.

R12 defines APP server deployment preparation rules, evidence model, restricted secret handling, validation gate, and GO / HOLD / NO-GO criteria before APP deployment can be considered. It does not execute deployment.

## Scope

R12 is documentation, registry JSON, evidence JSON, validation JSON, validator, final verification note, and release-index documentation only.

It defines target APP server references, backend service preparation, frontend static build preparation, Nginx / static serving preparation, PM2 / process manager preparation, runtime environment preparation, APP-to-DB dependency on R11, secret handling, healthcheck / smoke preparation, rollback preparation, Console International GA verification dependency, reviewer model, approver model, and preparation decision rules.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command.
- No executable shell script.
- No APP server connection.
- No APP server command execution.
- No backend command execution.
- No frontend command execution.
- No Nginx command execution.
- No PM2 command execution.
- No gunicorn command execution.
- No Flask command execution.
- No Node/npm command execution.
- No deployment.
- No install.
- No build execution.
- No restart.
- No APP runtime mutation.
- No DB server connection.
- No DB migration.
- No DB backup execution.
- No DB restore execution.
- No DB seed execution.
- No APP-to-DB live connection test.
- No APP server mutation.
- No DB server mutation.
- No auth mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No production config mutation.
- No production credential storage in public files.
- No actual APP deployment execution by this packet.

## Relationship with R1-R11

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
- R12: APP server deployment preparation pack.

R12 follows R11 and prepares APP deployment, but does not execute deployment.

## APP Deployment Preparation Model

The R12 evidence pack must preserve these core fields:

```json
{
  "packId": "server-precheck-r12-app-server-deployment-preparation-pack",
  "stage": "SERVER-PRECHECK-R12",
  "deploymentReadinessGateReference": "SERVER-PRECHECK-R10",
  "dbDeploymentPreparationReference": "SERVER-PRECHECK-R11",
  "approvalReference": "SERVER-PRECHECK-R7",
  "actualObservationEvidenceReference": "SERVER-PRECHECK-R9",
  "appDeploymentPerformedByThisPacket": false,
  "sshExecutedByThisPacket": false,
  "appServerConnectionPerformed": false,
  "appServerCommandExecuted": false,
  "backendCommandExecuted": false,
  "frontendCommandExecuted": false,
  "nginxCommandExecuted": false,
  "pm2CommandExecuted": false,
  "gunicornCommandExecuted": false,
  "flaskCommandExecuted": false,
  "nodeNpmCommandExecuted": false,
  "buildPerformed": false,
  "installPerformed": false,
  "restartPerformed": false,
  "dbServerConnectionPerformed": false,
  "dbMigrationPerformed": false,
  "dbBackupPerformed": false,
  "dbRestorePerformed": false,
  "dbSeedPerformed": false,
  "appToDbLiveConnectionTestPerformed": false,
  "serverMutationPerformed": false,
  "authMutationPerformed": false,
  "runtimeMutationPerformed": false,
  "frontendBackendMutationPerformed": false,
  "routeMutationPerformed": false,
  "productionConfigMutationPerformed": false,
  "targetAppServer": {
    "serverReference": "",
    "environmentName": "",
    "networkZoneReference": "",
    "deploymentPathReference": "",
    "runtimeUserReference": "",
    "accessBoundaryReference": ""
  },
  "backendPreparation": {
    "backendSourceReviewed": false,
    "backendEntryPointReviewed": false,
    "dependencyInventoryReviewed": false,
    "runtimeVersionPlanReviewed": false,
    "serviceStartPlanReviewed": false,
    "serviceHealthEndpointReviewed": false,
    "logPathPlanReviewed": false,
    "readinessStatus": "HOLD"
  },
  "frontendPreparation": {
    "frontendSourceReviewed": false,
    "staticBuildPlanReviewed": false,
    "buildExecutionAllowedByThisPacket": false,
    "distArtifactPlanReviewed": false,
    "routeFallbackPlanReviewed": false,
    "assetPathPlanReviewed": false,
    "readinessStatus": "HOLD"
  },
  "nginxPreparation": {
    "nginxStaticServingPlanReviewed": false,
    "reverseProxyPlanReviewed": false,
    "routeFallbackPlanReviewed": false,
    "tlsPlanReviewed": false,
    "nginxConfigMutationAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "processManagerPreparation": {
    "processManagerType": "PM2 | systemd | supervisor | manual | other",
    "processManagerPlanReviewed": false,
    "restartPolicyReviewed": false,
    "logRotationPlanReviewed": false,
    "processCommandExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "runtimeEnvironmentPreparation": {
    "environmentVariableInventoryReviewed": false,
    "productionEnvStoredInPublicPacket": false,
    "restrictedEnvReferenceOnly": true,
    "runtimePermissionPlanReviewed": false,
    "portPlanReviewed": false,
    "diskCapacityReviewed": false,
    "readinessStatus": "HOLD"
  },
  "appDbConnectionPreparation": {
    "dependsOnR11": true,
    "databaseUrlStoredInPublicPacket": false,
    "restrictedCredentialReferenceOnly": true,
    "appToDbConnectionPlanReviewed": false,
    "liveConnectionTestAllowedByThisPacket": false,
    "leastPrivilegeDependencyReviewed": false,
    "readinessStatus": "HOLD"
  },
  "healthcheckSmokePreparation": {
    "healthcheckPlanReviewed": false,
    "smokeTestPlanReviewed": false,
    "healthcheckExecutionAllowedByThisPacket": false,
    "smokeExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "rollbackPreparation": {
    "rollbackPlanRequired": true,
    "rollbackPlanReviewed": false,
    "previousArtifactRetentionReviewed": false,
    "rollbackExecutionAllowedByThisPacket": false,
    "readinessStatus": "HOLD"
  },
  "consoleGaVerificationDependency": {
    "required": true,
    "plannedStage": "SERVER-PRECHECK-R13",
    "runtimeVerificationCompleted": false,
    "menuArchitectureBaselineReference": "MENU-GA-R1/R2",
    "readinessStatus": "HOLD"
  },
  "secretHandling": {
    "productionAppSecretStoredInPublicPacket": false,
    "productionEnvStoredInPublicPacket": false,
    "databaseUrlStoredInPublicPacket": false,
    "jwtSecretStoredInPublicPacket": false,
    "apiKeyStoredInPublicPacket": false,
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

## APP Server Target Reference Requirements

The target APP server reference must document server reference, environment name, network zone reference, deployment path reference, runtime user reference, and access boundary reference.

R12 does not connect to the APP server and does not verify the target by executing commands.

## Backend Service Preparation Requirements

R12 defines, but does not execute:

- backend source review
- backend entry point review
- dependency inventory review
- runtime version plan review
- service start plan review
- health endpoint review
- log path plan review
- runtime user / permission plan review

R12 does not start backend services.

R12 does not run Flask, gunicorn, Python, Node, npm, or any server command.

R12 does not modify backend code.

R12 does not modify backend routes.

R12 does not modify backend config.

## Frontend Static Build Preparation Requirements

R12 defines, but does not execute:

- frontend source review
- static build plan review
- dist artifact plan review
- route fallback plan review
- asset path plan review
- deployment artifact source review

R12 does not run frontend build.

R12 does not run npm commands.

R12 does not modify frontend code.

R12 does not modify frontend routes.

R12 does not modify generated dist artifacts.

## Nginx / Static Serving Preparation Requirements

R12 defines, but does not execute:

- Nginx static serving plan
- reverse proxy plan if backend API proxy is required
- SPA route fallback plan
- TLS / certificate plan
- Nginx config restricted evidence reference
- static asset path mapping

R12 does not modify Nginx config.

R12 does not restart Nginx.

R12 does not reload Nginx.

R12 does not test production routes.

## PM2 / Process Manager Preparation Requirements

R12 defines, but does not execute:

- process manager type
- process start plan
- restart policy
- log rotation plan
- crash recovery plan
- process ownership / runtime user plan

R12 does not run PM2.

R12 does not start, stop, restart, reload, or mutate any process.

R12 does not generate executable process scripts.

## Runtime Environment Preparation Requirements

R12 defines runtime environment variable inventory review, restricted production environment reference handling, runtime permission plan review, port plan review, and disk capacity review.

Production .env content must not be stored in public docs, public JSON, or release index entries.

## APP-to-DB Connection Dependency on R11

APP-to-DB connection preparation depends on SERVER-PRECHECK-R11.

R12 does not test live APP-to-DB connectivity.

R12 does not store DATABASE_URL in public docs or JSON.

R12 does not connect to DB server.

Production DATABASE_URL must only be referenced through restricted evidence references.

APP DB credential handling must follow R11 DB server preparation rules.

## Secret and Production Env Handling Requirements

R12 prohibits public storage of:

- APP secret
- JWT secret
- API key
- DATABASE_URL
- DB password
- Flask secret key
- Session secret
- Private key
- SSH key
- Internal hostname
- Private IP
- Username
- Email
- Customer-specific server name
- Sensitive production path
- Production .env content

Secrets can only be represented by restricted evidence references.

Public release index must not include raw secrets or production .env content.

## Healthcheck / Smoke Preparation Requirements

R12 defines, but does not execute:

- healthcheck plan
- smoke test plan
- expected health endpoint reference
- APP static route verification plan
- backend API readiness plan
- log verification plan
- failure rollback condition

R12 does not execute healthcheck.

R12 does not execute smoke test.

R12 does not curl production endpoints.

R12 does not verify live production routes.

## Rollback Preparation Requirements

Rollback plan is required before APP deployment. R12 defines previous artifact retention review and rollback plan review but does not execute rollback.

## Console International GA Verification Dependency

R12 records Console runtime verification as a downstream gate:

SERVER-PRECHECK-R13 Console International GA Menu Runtime Verification

R13 should later verify:

- L1/L2 Sidebar menu completeness.
- L3 content-area menu behavior.
- Dashboard naming.
- Sidebar collapse / expand.
- International brand menu entries.
- IBMS upgraded menu entries.
- Role-based visibility.
- No Mock / Demo / Pilot / Coming soon language.
- Route coverage and page availability.

## GO / HOLD / NO-GO APP Preparation Rules

HOLD applies if the R10 deployment readiness gate is missing, R11 DB preparation is missing, target APP server reference is missing, backend preparation is incomplete, frontend preparation is incomplete, Nginx preparation is incomplete, process manager preparation is incomplete, runtime environment preparation is incomplete, APP-to-DB connection preparation is incomplete, secret handling is unresolved, rollback preparation is incomplete, healthcheck/smoke preparation is incomplete, Console GA runtime verification dependency is not planned, reviewer is missing, or approver is missing.

GO applies only if the R10 deployment readiness gate exists, R11 DB preparation exists, target APP server reference is documented, backend preparation is reviewed, frontend preparation is reviewed, Nginx/static serving preparation is reviewed, process manager preparation is reviewed, runtime environment preparation is reviewed, APP-to-DB connection plan is reviewed through R11 dependency, restricted secret handling is reviewed, rollback preparation is reviewed, healthcheck/smoke preparation is reviewed, no APP deployment or mutation occurred in R12, reviewer accepted, and approver status is GO.

NO-GO applies if APP deployment was performed by this packet, SSH execution was performed by this packet, APP server connection was performed by this packet, backend/frontend/Nginx/PM2/gunicorn/Flask/Node/npm command was executed by this packet, build/install/restart was performed by this packet, DB connection/migration/backup/restore/seed was performed by this packet, APP-to-DB live connection test was performed by this packet, server mutation is detected, auth/runtime/frontend/backend/route mutation is detected, production secret leakage is detected, R10/R11 evidence chain is rejected, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R10/R11/R7/R9 references, all false execution and mutation flags, build/Nginx/process/healthcheck/smoke/rollback/secret constraints, Console GA dependency, preparationDecision model, source markers, forbidden executable server, APP, frontend, backend, Nginx, PM2, and DB operation blocks, and the PASS marker.

## Boundary Statement

SERVER-PRECHECK-R12 records an APP server deployment preparation pack only.

It does not execute SSH, does not create SSH automation, does not include SSH connection commands, does not create executable shell scripts, does not connect to APP server, does not execute APP server, backend, frontend, Nginx, PM2, gunicorn, Flask, Node, npm, DB, healthcheck, smoke, build, install, restart, migration, backup, restore, or seed commands, does not test live APP-to-DB connectivity, does not mutate APP server, DB server, auth, runtime, frontend, backend, routes, production config, secrets, or server state, and does not perform actual APP deployment by this packet.

## PASS Marker

ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS
