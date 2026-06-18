# UCore Module Manifest Draft

## 1. Purpose

This file is the UCore A1 module manifest draft.
UCore is the primary name. IBMS Core, ibms-core, Core Operations, and Unified Core are historical wordings.

## 2. Scope

- docs-only
- manifest draft only
- governance-only alignment
- no runtime/API/DB/frontend implementation

## 3. Ownership Boundary

UCore owns core operation coordination context references and cross-module orchestration references.

UCore does not own Edge/Link/DB/Contracts runtime or schemas, and does not implement command-center runtime or auth/login/RBAC runtime in A1.

## 4. Foundation Relationship

Foundation Layer is reference-only in this task. UCore consumes shared foundation references through approved boundaries only.

## 5. A1 Boundary

UCore A1 does not create runtime, API, DB schema, menu route, or frontend page.
