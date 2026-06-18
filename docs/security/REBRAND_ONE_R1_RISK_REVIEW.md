# REBRAND ONE R1 Risk Review

## 1) Metadata mistaken as runtime readiness

- description: Metadata documents may be misread as approval for runtime migration.
- impact: Unauthorized runtime rename/move and transition-order break.
- control: Explicit readiness statements and "NOT_READY_*" gates in metadata/report files.
- current status: Controlled.

## 2) Version mistaken as GA release

- description: Transition versions may be interpreted as release versions.
- impact: Incorrect release communication and deployment expectations.
- control: Versioning file explicitly marks non-GA and non-runtime-ready status.
- current status: Controlled.

## 3) Package skeleton mistaken as package implementation

- description: 6+1 skeleton package list may be misunderstood as implemented runtimes.
- impact: Engineering planning drift and invalid dependency assumptions.
- control: Keep `SKELETON_ONLY` and `NOT_STARTED` runtime migration status in metadata.
- current status: Controlled.

## 4) Contracts partial coverage ignored

- description: Teams may proceed with runtime extraction without contracts baseline completion.
- impact: Schema/API drift and integration instability.
- control: Roadmap and transition index prioritize `CONTRACTS-A0-MANIFEST-BASELINE`.
- current status: Open but explicitly tracked.

## 5) Edge source missing ignored

- description: EDGE extraction may start without source audit.
- impact: Incomplete migration, protocol break, and unknown runtime gaps.
- control: Roadmap declares `EDGE-SOURCE-AUDIT` as immediate optional parallel task before extraction.
- current status: Open but explicitly tracked.

## 6) API/DB rename started too early

- description: Rebrand momentum can trigger premature namespace/table renaming.
- impact: Compatibility break and rollback complexity.
- control: Maintain "NOT_READY_FOR_DB_RENAME" and "NOT_READY_FOR_API_NAMESPACE_CHANGE" gates.
- current status: Controlled.

## 7) Legacy IBMS source base removed too early

- description: Legacy source base may be treated as obsolete before approved migration.
- impact: Loss of migration source, audit traceability, and compatibility reference.
- control: Metadata policy keeps `AN_VANTARIS_IBMS` as source base until approved migration.
- current status: Controlled.

## 8) UFMS boundary weakened

- description: Platform docs may accidentally normalize UFMS runtime/source/schema reuse.
- impact: Cross-system contamination and governance violation.
- control: Keep UFMS references boundary-only and prohibit runtime/source/schema/auth/login/seed/migration mixing.
- current status: Controlled, no contamination detected in R1 outputs.

## 9) Roadmap task order bypassed

- description: Teams may skip sequencing and start package/runtime work directly.
- impact: Rework, inconsistent artifacts, and governance drift.
- control: Explicit recommended sequence in roadmap and transition index.
- current status: Controlled by documentation, execution enforcement required in next tasks.
