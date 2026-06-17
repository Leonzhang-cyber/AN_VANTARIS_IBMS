# IBMS / UFMS Cross-Contamination Risk Review

## 1. Risk

IBMS and UFMS are developed in parallel. Mixing source code, routes, database schema, menu definitions, auth logic, or seed logic can create unstable builds, incorrect product behavior, and security boundary violations.

## 2. High-Risk Areas

- authentication and JWT logic
- database schema, seed, migration
- menu and routing
- backend APIs
- frontend services
- environment configuration
- deployment scripts
- raw source packages

## 3. Controls

- stop immediately when UFMS content is found in an IBMS task
- require explicit user approval before cross-system work
- keep contracts/API documents as the integration boundary
- keep commits small and scoped
- keep working tree clean after each task

## 4. Enforcement

Every IBMS task must include boundary checks before modifying files. If a boundary conflict is detected, no file should be changed until the user confirms.
