# SERVER-PRECHECK-R8 Manual Observation Evidence Packet

PASS marker: ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS

## Purpose

SERVER-PRECHECK-R8 defines the manual observation evidence packet used after a separately approved manual read-only observation.

R8 does not perform observation. It records the evidence format, redaction checklist, archive requirements, reviewer model, approver model, and GO / HOLD / NO-GO closure decision rules.

## Scope

R8 is documentation, registry, evidence JSON, validation JSON, validator, and release-index verification only.

The packet is for post-observation evidence handling only. It does not authorize access, does not connect to a server, and does not provide any server connection command.

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
- No actual observation execution.

## Relationship with R1-R7F

- SERVER-PRECHECK-R1 established the dual-server read-only audit baseline.
- SERVER-PRECHECK-R2 established the approved read-only access window plan.
- SERVER-PRECHECK-R3 established the actual approved read-only observation plan candidate.
- SERVER-PRECHECK-R4 established the read-only execution approval packet.
- SERVER-PRECHECK-R4F recorded R4 final verification.
- SERVER-PRECHECK-R5 established the actual read-only observation entry gate.
- SERVER-PRECHECK-R5F recorded R5 final verification.
- SERVER-PRECHECK-R6 established the manual read-only observation command pack.
- SERVER-PRECHECK-R6F recorded R6 final verification.
- SERVER-PRECHECK-R7 established the human approval record and observation window lock.
- SERVER-PRECHECK-R7F recorded R7 final verification.

R8 depends on the R7 approval and observation window reference, but this R8 artifact remains an evidence packet definition only.

## Manual Observation Evidence Model

The evidence packet must record the observation approval reference, observation window reference, observer, approver, target scope, approved services, approved paths, observation time window, redaction state, archive location, review status, and final closure decision.

The default packet status is NOT_EXECUTED. The default review status is HOLD. The default closure decision is HOLD.

## Evidence Record Required Fields

The evidence packet must preserve these core fields:

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
  "redactionChecklist": [],
  "archiveLocation": "",
  "reviewStatus": "HOLD",
  "closureDecision": "HOLD",
  "notes": ""
}
```

Additional traceability fields may be added, but these core fields must not be removed.

## Evidence Item Model

Each evidence item must support:

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

## Redaction Requirements

Raw evidence is not archived by default.

Only redacted evidence can be accepted into the public release packet.

The redaction checklist must cover:

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

If raw evidence must be retained, it must be treated as restricted-access evidence and excluded from the public release index.

## Archive Requirements

- Evidence packet becomes immutable after acceptance.
- Evidence must link back to the R7 approval record.
- Evidence must include the observation window reference.
- Evidence must record observer, reviewer, and approver.
- Evidence must include redaction status.
- Evidence must include final closure decision.
- Public release index must not include secrets or raw sensitive evidence.

## Review and Approval Requirements

The reviewer must confirm that evidence items are complete, redaction status is recorded, public artifacts are redacted, and no mutation occurred.

The approver must confirm that the R7 approval reference exists, the R7 observation window is linked, and the final closure decision is one of HOLD, GO, or NO-GO.

## GO / HOLD / NO-GO Closure Rules

HOLD applies if evidence is incomplete, approval is missing, redaction is incomplete, the observation window does not match R7, or the reviewer is not assigned.

GO applies only if the approval reference exists, the observation window is linked to R7, evidence items are complete, required redaction is completed, no mutation occurred, and review is accepted.

NO-GO applies if access occurred outside the approved window, mutation is detected, secret leakage is detected, unredacted raw evidence is included in the public packet, the approver rejects the packet, or an R6/R7 boundary is violated.

## Validator Requirements

The validator must check required R8 files, JSON parseability, stage, approval reference, observation window reference, read-only boundary flags, evidence item list, redaction checklist, review status model, closure decision model, source markers, and the PASS marker.

## Boundary Statement

SERVER-PRECHECK-R8 records a manual observation evidence packet only.

It does not execute SSH, does not create SSH automation, does not include SSH connection commands, does not create executable shell scripts, does not deploy, does not install, does not mutate APP server, DB server, DB migration state, auth, runtime, frontend, backend, routes, production config, secrets, or any server state, and does not perform actual observation.

## PASS Marker

ONE_SERVER_PRECHECK_R8_MANUAL_OBSERVATION_EVIDENCE_PACKET_PASS
