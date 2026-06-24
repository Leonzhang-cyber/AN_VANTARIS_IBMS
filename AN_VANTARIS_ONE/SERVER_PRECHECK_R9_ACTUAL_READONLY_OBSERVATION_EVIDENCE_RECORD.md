# SERVER-PRECHECK-R9 Actual Read-only Observation Evidence Record Format

PASS marker: ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS

## Status

This file defines the evidence record format for actual manual read-only observation results.

It is not an execution plan. It does not perform observation. It does not include server connection commands. It does not authorize APP or DB checks.

## Evidence Record Template

```json
{
  "recordId": "server-precheck-r9-actual-readonly-observation-evidence-record",
  "stage": "SERVER-PRECHECK-R9",
  "approvalReference": "SERVER-PRECHECK-R7",
  "evidencePacketReference": "SERVER-PRECHECK-R8",
  "observationPlanReference": "SERVER-PRECHECK-R3",
  "manualCommandPackReference": "SERVER-PRECHECK-R6",
  "observationPerformedByThisPacket": false,
  "sshExecutedByThisPacket": false,
  "serverMutationPerformed": false,
  "dbMutationPerformed": false,
  "authMutationPerformed": false,
  "runtimeMutationPerformed": false,
  "frontendBackendMutationPerformed": false,
  "deploymentPerformed": false,
  "installPerformed": false,
  "observationStatus": "NOT_RECORDED",
  "observationWindowStatus": "LOCKED_BY_R7",
  "observer": {
    "name": "",
    "role": "",
    "organization": ""
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
  "targetEnvironment": {
    "environmentName": "",
    "appServerReference": "",
    "dbServerReference": "",
    "networkZoneReference": ""
  },
  "observationSession": {
    "sessionId": "",
    "startedAt": "",
    "endedAt": "",
    "withinApprovedWindow": false,
    "r7WindowReference": "",
    "r6CommandPackUsed": false,
    "manualReadonlyOnly": true
  },
  "appServerEvidence": [],
  "dbServerEvidence": [],
  "crossServerEvidence": [],
  "redactionChecklist": [
    "Password",
    "Token",
    "API key",
    "JWT",
    "Private key",
    "Secret",
    "SSH key",
    "Database URL",
    "Internal hostname",
    "Private IP",
    "Username",
    "Email",
    "Customer-specific server name",
    "Production path with sensitive naming"
  ],
  "restrictedEvidenceReferences": [],
  "publicEvidenceReferences": [],
  "findingSummary": {
    "criticalFindings": 0,
    "majorFindings": 0,
    "minorFindings": 0,
    "informationalFindings": 0
  },
  "closureDecision": "HOLD",
  "notes": ""
}
```

## APP Server Evidence Item Template

```json
{
  "evidenceId": "",
  "serverRole": "APP",
  "evidenceType": "service-health",
  "sourceDescription": "",
  "collectionMode": "manual-readonly",
  "actualCommandTextStored": false,
  "rawOutputStored": false,
  "redactedOutputStored": true,
  "redactedArtifactReference": "",
  "containsSecret": false,
  "containsCredential": false,
  "containsToken": false,
  "containsPrivateIp": false,
  "containsHostname": false,
  "containsUsername": false,
  "observationResult": "NOT_RECORDED",
  "findingSeverity": "INFORMATIONAL",
  "reviewStatus": "PENDING",
  "reviewerNotes": ""
}
```

## DB Server Evidence Item Template

```json
{
  "evidenceId": "",
  "serverRole": "DB",
  "evidenceType": "database-health",
  "sourceDescription": "",
  "collectionMode": "manual-readonly",
  "actualCommandTextStored": false,
  "rawOutputStored": false,
  "redactedOutputStored": true,
  "redactedArtifactReference": "",
  "containsSecret": false,
  "containsCredential": false,
  "containsToken": false,
  "containsPrivateIp": false,
  "containsHostname": false,
  "containsUsername": false,
  "observationResult": "NOT_RECORDED",
  "findingSeverity": "INFORMATIONAL",
  "reviewStatus": "PENDING",
  "reviewerNotes": ""
}
```

## Public and Restricted Evidence Rules

Raw evidence is not archived in the public release packet.

Actual command text is not stored by default.

Public evidence references must point only to redacted output artifacts.

Restricted evidence references are for restricted-access raw material, if a future approved process retains it outside the public release index.

## Boundary Confirmation

- observationPerformedByThisPacket: false
- sshExecutedByThisPacket: false
- serverMutationPerformed: false
- dbMutationPerformed: false
- authMutationPerformed: false
- runtimeMutationPerformed: false
- frontendBackendMutationPerformed: false
- deploymentPerformed: false
- installPerformed: false
- observationWindowStatus: LOCKED_BY_R7
- manualReadonlyOnly: true

## Final Status

ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS
