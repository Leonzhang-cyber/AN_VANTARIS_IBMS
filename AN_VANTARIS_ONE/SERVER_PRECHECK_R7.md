# SERVER-PRECHECK-R7 Human Approval Record and Observation Window Lock

PASS marker: ONE_SERVER_PRECHECK_R7_HUMAN_APPROVAL_RECORD_AND_OBSERVATION_WINDOW_LOCK_PASS

## Purpose

SERVER-PRECHECK-R7 records the human approval structure and locks the observation window metadata before any future manual read-only observation may be considered.

R7 does not execute SSH.
R7 does not create SSH automation.
R7 does not include SSH connection commands.
R7 does not add or modify observation commands.
R7 does not deploy, install, restart, stop, start, modify DB, modify auth, or mutate runtime.

## Relationship to Previous Tasks

- R4: Read-only SSH execution approval packet.
- R4F: R4 final verification and release index update.
- R5: Actual read-only observation entry gate.
- R5F: R5 final verification and release index update.
- R6: Manual read-only observation command pack.
- R6F: R6 final verification and release index update.
- R7: Human approval record and observation window lock.

R7 records approval metadata only. It does not authorize automatic execution.

## Required Approval Record Fields

The approval record must define:

- approvalStatus
- approverName
- approverRole
- operatorName
- operatorRole
- observationWindowStart
- observationWindowEnd
- targetServerIdentity
- targetServerRole
- approvedServices
- approvedPaths
- approvedNonSecretFiles
- approvedEvidenceLocation
- redactionPolicy
- stopConditions
- noGoConditions
- approvalRecordedAt

## Approval Status Model

Allowed values:

- HOLD
- GO
- NO-GO

Default approvalStatus is HOLD.

GO cannot be assumed. A future human-approved observation may only proceed if all required fields are completed and no stop condition exists.

## Observation Window Lock

The observation window must be locked before any later manual read-only observation.

The lock must include:

- exact start time
- exact end time
- timezone
- approver
- operator
- target server identity
- approved scope

No observation may occur outside the locked window.

## Stop Conditions

Stop immediately if:

- approver is missing
- operator is missing
- target server identity is unclear
- observation window is missing or expired
- approved service scope is unclear
- approved path scope is unclear
- evidence location is unclear
- redaction policy is missing
- any password, token, secret, private key, or credential is requested
- any write, restart, stop, start, install, deploy, DB, auth, or runtime mutation is requested
- any SSH automation is introduced

## Boundary Statement

SERVER-PRECHECK-R7 records approval metadata and observation window lock only.

It does not execute SSH, does not create SSH automation, does not include SSH connection commands, does not create executable scripts, does not change R6 command pack, does not create frontend/backend/routes, does not deploy, does not install, does not modify DB/auth/secrets/runtime, and does not authorize automatic server access.

## Next Task If Approved

If R7 is accepted and a real human approval is later recorded, the next task may be:

SERVER-PRECHECK-R8 Manual Observation Evidence Packet

R8 must still avoid automatic execution and should only define how manually collected evidence is recorded and redacted.

## Final Status

ONE_SERVER_PRECHECK_R7_HUMAN_APPROVAL_RECORD_AND_OBSERVATION_WINDOW_LOCK_PASS
