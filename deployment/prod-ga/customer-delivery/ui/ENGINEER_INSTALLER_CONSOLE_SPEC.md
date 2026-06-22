# Engineer Installer Console Specification

This is a specification-only UI entry for engineer-led customer delivery. It does not implement live backend mutation, service control, DB migration, or runtime activation.

## Engineer-only cards

1. Package Import — shows R8 tarball path, checksum, import status, and offline package location.
2. System Precheck — displays OS, disk, package counts, forbidden scan, and dry-run status.
3. DB Readiness — shows DB package count and migration plan status without running migrations.
4. EDGE Readiness — shows EDGE package count, runtime/source folder presence, and activation locked state.
5. LINK Readiness — shows LINK package count and activation locked state.
6. Contracts Validation — shows Contracts package count and schema validation boundary status.
7. Install Dry-run — displays planned installation steps and required future approvals.
8. Verify — displays package integrity, PASS marker, report, and manifest validation status.
9. Rollback Dry-run — displays rollback rehearsal steps without deletion or state mutation.
10. Evidence Export — lists evidence artifacts to collect for acceptance.
11. Activation Approval — shows locked approval gates for future production activation.

## Safety behavior

- All cards are read-only by default.
- No POST, PUT, PATCH, DELETE, shell execution, service start, DB migration, or runtime activation is available in R9.
- Execution controls are represented as future locked approval gates only.
