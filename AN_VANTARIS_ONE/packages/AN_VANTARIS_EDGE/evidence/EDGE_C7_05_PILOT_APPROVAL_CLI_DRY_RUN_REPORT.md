# UFMS-EDGE-C7-05 Pilot Approval CLI Dry-run Report

## 1. Scope

This report records C7-05 Pilot Approval CLI Dry-run.

C7-05 adds a local CLI dry-run that reads pilot approval packet fixtures and outputs approve or reject decisions.

C7-05 does not write runtime state.

C7-05 does not modify connectors.

C7-05 does not enable a real endpoint.

C7-05 does not introduce package dependencies.

## 2. Artifacts

Created:

- scripts/validation/edge-c7-pilot-approval-cli-dry-run.sh
- scripts/validation/lib/pilot-approval-cli-dry-run.cjs

## 3. CLI Behavior

The CLI validates pilot approval packets against C7 JSON schemas and dry-run boundary checks.

Expected fixture decisions:

- pilot-approval-packet.valid.sample.json: APPROVE_DRY_RUN
- pilot-approval-packet.invalid-inline-secret.sample.json: REJECT_DRY_RUN
- pilot-approval-packet.invalid-runtime-approved.sample.json: REJECT_DRY_RUN

## 4. Boundary

The CLI enforces:

- runtimeEnablementApproved=false
- productionApproved=false
- no unsafe secret markers
- schema-valid endpoint approval
- schema-valid credential reference
- schema-valid rollback plan
- schema-valid operator authorization
- schema-valid evidence collection

## 5. Decision

UFMS_EDGE_C7_05_PILOT_APPROVAL_CLI_DRY_RUN_PASS

This is dry-run decisioning only.

Pilot is not approved.

Production is not approved.

Runtime is not enabled.
