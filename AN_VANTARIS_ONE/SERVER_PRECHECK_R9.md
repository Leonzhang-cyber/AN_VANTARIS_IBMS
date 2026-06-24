# SERVER-PRECHECK-R9 Actual Read-only Observation Evidence Record

PASS marker: ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS

## Purpose

SERVER-PRECHECK-R9 defines the formal evidence record for actual manual read-only observation results.

R9 is the first server-precheck stage that models actual observation result evidence, but it does not execute the observation. It records how separately approved human read-only observation results are represented, reviewed, redacted, closed, and validated.

## Scope

R9 is documentation, registry JSON, evidence JSON, validation JSON, validator, final verification note, and release-index documentation only.

It defines APP server evidence fields, DB server evidence fields, cross-server evidence references, redaction rules, restricted evidence references, public evidence references, finding summary, reviewer requirements, approver requirements, and closure rules.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command.
- No executable shell script.
- No deployment.
- No install.
- No APP server mutation.
- No DB server mutation.
- No DB migration.
- No auth mutation.
- No runtime mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No production config mutation.
- No actual observation execution by this packet.

## Relationship with R1-R8

- R1: Dual-server read-only audit.
- R2: Read-only access window plan.
- R3: Actual read-only observation plan.
- R4: Read-only SSH execution approval packet.
- R5: Actual read-only observation entry gate.
- R6: Manual read-only observation command pack.
- R7: Human approval record and observation window lock.
- R8: Manual observation evidence packet.
- R9: Actual read-only observation evidence record.

R9 references R7 for approval and window lock, R8 for evidence packet structure, R3 for the observation plan, and R6 for the manual read-only command pack. It does not provide a connection method or execute server checks.

## Actual Read-only Observation Evidence Record Model

The R9 evidence record must preserve these core fields:

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
  "redactionChecklist": [],
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

Additional traceability fields may be added, but the core boundary fields must not be removed.

## Observation Session Record

The observation session record links the evidence record to the separately approved R7 observation window and the R6 manual read-only command pack.

The default session state is not recorded, outside proof of approved window not yet confirmed, R6 command pack not yet marked as used, and manualReadonlyOnly true.

## APP Server Observation Evidence Fields

APP server evidence items must use this model:

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

Allowed APP evidence types:

- service-health
- runtime-process
- app-port-listen
- nginx-static-route
- pm2-process-summary
- env-presence-check
- log-excerpt-redacted
- disk-space-summary
- permission-summary
- other

## DB Server Observation Evidence Fields

DB server evidence items must use this model:

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

Allowed DB evidence types:

- database-health
- postgres-service-status
- database-connectivity-readonly
- schema-presence-summary
- migration-state-summary
- backup-presence-summary
- disk-space-summary
- permission-summary
- log-excerpt-redacted
- other

## Redaction and Restricted Evidence Rules

Raw evidence is not archived in the public release packet.

Actual command text is not stored by default.

Only redacted output references can be included in the public release index.

Restricted raw evidence, if retained, must be referenced only by restrictedEvidenceReferences.

Public release index must not include secrets, credentials, tokens, private keys, DB URLs, private IPs, usernames, emails, customer-specific server names, or sensitive production paths.

The redaction checklist must include:

- Password
- Token
- API key
- JWT
- Private key
- Secret
- SSH key
- Database URL
- Internal hostname
- Private IP
- Username
- Email
- Customer-specific server name
- Production path with sensitive naming

## Observation Result Classification

Allowed observationStatus values:

- NOT_RECORDED
- RECORDED
- PARTIAL
- ABORTED
- REJECTED

Allowed observationResult values:

- NOT_RECORDED
- PASS
- WARN
- FAIL
- NOT_APPLICABLE

Allowed findingSeverity values:

- CRITICAL
- MAJOR
- MINOR
- INFORMATIONAL
- NONE

Allowed reviewStatus values:

- PENDING
- ACCEPTED
- REJECTED

Allowed approvalStatus values:

- HOLD
- GO
- NO-GO

Allowed closureDecision values:

- HOLD
- GO
- NO-GO

## Reviewer and Approver Requirements

The reviewer must confirm that APP evidence, DB evidence, cross-server evidence, redaction status, restricted evidence references, public evidence references, and finding summary are complete for the recorded observation state.

The approver must confirm that the R7 approval reference exists, the R8 evidence packet reference exists, the observation session is within the approved R7 window before GO, and no mutation or unredacted public evidence is present.

## GO / HOLD / NO-GO Closure Rules

HOLD applies if observation evidence is not recorded, R7 approval reference is missing, R8 evidence packet reference is missing, observation window is not confirmed, reviewer is missing, redaction is incomplete, APP or DB evidence is incomplete, or any evidence item remains PENDING.

GO applies only if the R7 approval reference exists, the R8 evidence packet reference exists, the observation session is within the approved R7 window, APP and DB server evidence are recorded, all public evidence is redacted, no mutation occurred, reviewer accepted evidence, and approver status is GO.

NO-GO applies if SSH occurred outside the approved R7 window, mutation is detected, deployment or install is detected, DB migration is detected, auth/runtime/frontend/backend mutation is detected, unredacted raw evidence is included in the public packet, secret leakage is detected, reviewer rejected evidence, approver status is NO-GO, or an R6/R7/R8 boundary is violated.

## Validator Requirements

The validator must check required files, JSON parseability, stage, R7/R8/R3/R6 references, execution and mutation flags, observationWindowStatus, manualReadonlyOnly, APP and DB evidence lists, redaction checklist, restricted and public evidence references, closure decision model, source markers, forbidden executable server operation blocks, and the PASS marker.

## Boundary Statement

SERVER-PRECHECK-R9 records the evidence model for actual manual read-only observation results only.

It does not execute SSH, does not create SSH automation, does not include SSH connection commands, does not create executable shell scripts, does not deploy, does not install, does not mutate APP server, DB server, DB migration state, auth, runtime, frontend, backend, routes, production config, secrets, or server state, and does not perform actual observation by this packet.

## PASS Marker

ONE_SERVER_PRECHECK_R9_ACTUAL_READONLY_OBSERVATION_EVIDENCE_RECORD_PASS
