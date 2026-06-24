# SERVER-PRECHECK-R12 APP Server Deployment Preparation Pack Format

PASS marker: ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS

## Status

This file defines the APP server deployment preparation pack format after the R11 DB server deployment preparation pack.

It is not an APP deployment plan. It does not connect to APP server. It does not execute backend, frontend, Nginx, PM2, gunicorn, Flask, Node, npm, DB, build, install, restart, healthcheck, or smoke commands.

## Preparation Pack Template

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

## Decision Status Values

Readiness status values:

- HOLD
- GO
- NO-GO

Reviewer status values:

- PENDING
- ACCEPTED
- REJECTED

Approver status values:

- HOLD
- GO
- NO-GO

Preparation decision values:

- HOLD
- GO
- NO-GO

## Boundary Confirmation

- appDeploymentPerformedByThisPacket: false
- sshExecutedByThisPacket: false
- appServerConnectionPerformed: false
- appServerCommandExecuted: false
- backendCommandExecuted: false
- frontendCommandExecuted: false
- nginxCommandExecuted: false
- pm2CommandExecuted: false
- gunicornCommandExecuted: false
- flaskCommandExecuted: false
- nodeNpmCommandExecuted: false
- buildPerformed: false
- installPerformed: false
- restartPerformed: false
- dbServerConnectionPerformed: false
- dbMigrationPerformed: false
- dbBackupPerformed: false
- dbRestorePerformed: false
- dbSeedPerformed: false
- appToDbLiveConnectionTestPerformed: false
- buildExecutionAllowedByThisPacket: false
- nginxConfigMutationAllowedByThisPacket: false
- processCommandExecutionAllowedByThisPacket: false
- liveConnectionTestAllowedByThisPacket: false
- healthcheckExecutionAllowedByThisPacket: false
- smokeExecutionAllowedByThisPacket: false
- rollbackExecutionAllowedByThisPacket: false
- restrictedSecretReferenceOnly: true

## Final Status

ONE_SERVER_PRECHECK_R12_APP_SERVER_DEPLOYMENT_PREPARATION_PACK_PASS
