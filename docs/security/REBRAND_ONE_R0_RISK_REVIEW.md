# REBRAND-ONE-R0 Risk Review

## 1) Accidental global replace

- Description: Broad `IBMS -> ONE` replacement can corrupt technical identifiers and historical records.
- Impact: Broken references, invalid docs, and migration confusion.
- Control: Manual scoped edits only; no global replace.
- Current Status: Controlled in R0.

## 2) Runtime rename confusion

- Description: Readers may assume docs rebrand means runtime/package rename is approved.
- Impact: Unauthorized source/package moves and unstable transition sequencing.
- Control: Explicit "docs-only" and "runtime rename not approved" statements in current entry docs.
- Current Status: Controlled in R0.

## 3) Legacy compatibility confusion

- Description: Rebranding can blur distinction between platform name and legacy source system.
- Impact: Migration-source misuse and incorrect compatibility assumptions.
- Control: Keep `AN_VANTARIS_IBMS` identified as legacy/current implementation base; keep legacy wording in historical evidence.
- Current Status: Controlled with documented scope.

## 4) DB/API naming break

- Description: Product wording edits can accidentally trigger API path or DB table naming edits.
- Impact: Client integration break, migration divergence, and rollback risk.
- Control: Explicit prohibition on API/DB/route/migration rename in R0; validation checks after edits.
- Current Status: Controlled; no DB/API rename in this task.

## 5) Customer-facing naming inconsistency

- Description: Mixed platform naming across entry docs can create messaging inconsistency.
- Impact: Stakeholder confusion and weak brand clarity.
- Control: Align current platform-entry documents to `VANTARIS ONE`; keep module language as `ibms-core`.
- Current Status: Improved in R0.

## 6) IBMS module deletion risk

- Description: Misinterpreting rebrand as replacement can lead to removal of IBMS domain/module references.
- Impact: Loss of business-domain continuity and migration mapping integrity.
- Control: Preserve IBMS as `ibms-core` business module and keep legacy-source traceability docs.
- Current Status: Controlled; IBMS module retained.

## 7) UFMS contamination risk

- Description: Rebrand edits may accidentally introduce UFMS runtime/source/schema/auth/login/seed/migration instructions.
- Impact: Cross-system boundary breach and architecture contamination.
- Control: Boundary guard enforcement; UFMS allowed only as boundary/adapter/prohibition context in docs.
- Current Status: No contamination detected in R0 outputs.
