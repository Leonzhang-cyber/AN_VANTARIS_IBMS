# IBMS / UFMS Boundary Guard

## 1. Purpose

IBMS and UFMS are separate systems developed in parallel. Their source code, runtime configuration, database schema, menu definitions, API routes, seed data, and documentation must not be mixed unless explicitly approved.

## 2. Default Boundary

- IBMS tasks operate only inside AN_VANTARIS_IBMS.
- UFMS tasks operate only inside the UFMS repository.
- Raw source packages are read-only unless a task explicitly approves migration.
- Cross-system integration must use contracts, API documents, or integration specifications.

## 3. Immediate Stop Rule

During any IBMS task, if any UFMS-specific content is discovered, the executor must stop immediately and report it before continuing.

Stop examples:

- UFMS path or repository detected
- UFMS menu naming detected
- UFMS API route copied into IBMS
- UFMS database schema or migration appears in IBMS
- UFMS seed/auth/login logic appears in IBMS
- UFMS documentation is being merged into IBMS
- ambiguous IBMS/UFMS naming conflict

## 4. Prohibited Actions

- Do not copy UFMS source into IBMS.
- Do not copy IBMS source into UFMS.
- Do not reuse UFMS auth, seed, migration, database, route, or menu logic inside IBMS without explicit approval.
- Do not rename IBMS modules to UFMS names.
- Do not silently resolve cross-system conflicts.

## 5. Allowed Cross-System Work

Allowed only when user explicitly approves:

- API contract alignment
- integration protocol documentation
- data mapping documentation
- EdgeLink / IBMS / UFMS interface documents
- read-only comparison reports

## 6. Required Report When Boundary Risk Is Found

Report:

- detected file/path
- detected UFMS/IBMS conflicting content
- why it is risky
- recommended action
- wait for user instruction
