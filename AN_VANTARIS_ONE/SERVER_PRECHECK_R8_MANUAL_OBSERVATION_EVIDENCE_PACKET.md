# SERVER-PRECHECK-R8 Manual Observation Evidence Packet Format

PASS marker: ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS

## Status

This file defines the manual observation evidence packet format used after a separately approved manual read-only observation.

It is not an execution plan. It is not an observation command pack. It does not include server connection commands. It does not authorize observation.

## Evidence Packet Template

```json
{
  "packetId": "server-precheck-r8-manual-observation-evidence-packet",
  "stage": "SERVER-PRECHECK-R8",
  "approvalReference": "SERVER-PRECHECK-R7",
  "observationWindowReference": "SERVER-PRECHECK-R7",
  "observationStatus": "NOT_EXECUTED",
  "observer": {
    "name": "",
    "role": "",
    "organization": ""
  },
  "approver": {
    "name": "",
    "role": "",
    "approvalStatus": "HOLD"
  },
  "targetServers": [],
  "approvedServices": [],
  "approvedPaths": [],
  "observationStartTime": "",
  "observationEndTime": "",
  "commandsReviewedOnly": true,
  "sshExecutedByThisPacket": false,
  "serverMutationPerformed": false,
  "dbMutationPerformed": false,
  "authMutationPerformed": false,
  "runtimeMutationPerformed": false,
  "rawEvidenceAllowed": false,
  "redactedEvidenceRequired": true,
  "evidenceItems": [],
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
  "archiveLocation": "",
  "reviewStatus": "HOLD",
  "closureDecision": "HOLD",
  "notes": ""
}
```

## Evidence Item Template

```json
{
  "evidenceId": "",
  "sourceType": "terminal-output",
  "sourceDescription": "",
  "collectionMethod": "manual-readonly",
  "containsSecret": false,
  "containsCredential": false,
  "containsToken": false,
  "containsPrivateIp": false,
  "containsHostname": false,
  "containsUsername": false,
  "redactionStatus": "REQUIRED",
  "redactedArtifactReference": "",
  "reviewStatus": "PENDING",
  "reviewerNotes": ""
}
```

## Allowed Models

Allowed sourceType values:

- terminal-output
- screenshot
- config-snapshot
- service-status
- log-excerpt
- checklist
- other

Allowed redactionStatus values:

- NOT_REQUIRED
- REQUIRED
- COMPLETED
- REJECTED

Allowed reviewStatus values:

- PENDING
- ACCEPTED
- REJECTED

Allowed packet reviewStatus values:

- HOLD
- ACCEPTED
- REJECTED

Allowed closureDecision values:

- HOLD
- GO
- NO-GO

## Redaction and Archive Rules

Raw evidence is not archived by default.

Only redacted evidence can be accepted into the public release packet.

Restricted-access raw evidence, if retained by a future authorized process, must be excluded from the public release index.

The accepted packet must be immutable after acceptance and must link back to SERVER-PRECHECK-R7 approval and observation window references.

## Boundary Confirmation

- sshExecutedByThisPacket: false
- serverMutationPerformed: false
- dbMutationPerformed: false
- authMutationPerformed: false
- runtimeMutationPerformed: false
- rawEvidenceAllowed: false
- redactedEvidenceRequired: true

## Final Status

ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS
