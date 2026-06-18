# IBMS Core Runtime Migration Plan

## Stage 0 — Current legacy runtime remains stable

- `AN_VANTARIS_IBMS-backend` remains current runtime
- `AN_VANTARIS_IBMS-frontend` remains current UI runtime
- no runtime move in A6

## Stage 1 — module boundary tagging

- classify backend APIs by target module
- classify frontend routes by target module
- mark driver extraction candidates
- mark platform-core candidates

## Stage 2 — compatibility wrapper

- introduce module-level API adapter
- keep legacy path alive
- add new namespace only after Contracts approval

## Stage 3 — ibms-core package extraction

- create `ibms-core` under `AN_VANTARIS_Code` after readiness
- move only business views/services
- leave platform-core, Edge, Link, DB, NexusAI outside

## Stage 4 — menu and license binding

- register `ibms-core` as module
- bind license feature
- bind menu entries
- bind role permissions

## Stage 5 — DB domain alignment

- map existing tables to domain
- no direct rename first
- migration only through `AN_VANTARIS_DB`

## Stage 6 — legacy deprecation

- deprecated only after compatibility test
- removal only after GA owner approval

## Rollback Rules

- each stage has separate commit
- no mixed DB/API/UI/package migration
- keep legacy branch/tag before runtime move
- evidence report required
