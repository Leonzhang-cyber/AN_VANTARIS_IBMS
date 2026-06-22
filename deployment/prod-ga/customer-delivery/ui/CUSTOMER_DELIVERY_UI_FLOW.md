# Customer Delivery UI Flow

This document defines the customer-facing delivery flow for review and acceptance. It is a specification-only flow and does not add live UI runtime behavior.

## Flow stages

1. Readiness Review
   - Review EDGE, LINK, DB, and Contracts package readiness.
   - Confirm package counts and forbidden scan status.

2. Deployment Window Approval
   - Confirm planned deployment window, support team availability, backups, and rollback authority.

3. Activation Approval
   - Confirm explicit approval for any future production activation.
   - R9 does not execute activation.

4. Acceptance Evidence Review
   - Review precheck, dry-run install, verify, rollback dry-run, checksum, and package count evidence.

5. Handover
   - Confirm acceptance signer, operational owner, known limitations, and next-phase activation plan.

## Customer-visible safety statement

Customer production activation is not executed in this delivery scaffold. Install, rollback, DB migration, EDGE/LINK runtime activation, and service control remain locked until a future explicitly approved phase.
