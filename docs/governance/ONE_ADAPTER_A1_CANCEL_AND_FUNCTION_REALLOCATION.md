# ONE Adapter A1 Cancel And Function Reallocation

## 1. Cancellation Objective

Formally cancel ONE Adapter as an active VANTARIS ONE module and reallocate its useful responsibilities to the correct system owners.

## 2. Architecture Decision

ONE Adapter is cancelled as a VANTARIS ONE module.
ONE Adapter is not a platform module.
ONE Adapter is not middleware.
ONE Adapter is not a future implementation gate.

## 3. Reason For Cancellation

- low practical engineering value
- duplicates EDGE/LINK/Contracts/UCDE/DB responsibilities
- adds an unnecessary middle layer
- increases boundary ambiguity
- risks becoming a monolithic adapter

## 4. Removed Module

- removed from active platform topology: `one-adapter` (kept only as historical/deprecated documentation record)

## 5. Replacement Model

External systems -> EDGE Fleet -> LINK -> Shared Foundation outputs -> VANTARIS ONE modules

## 6. Function Reallocation Summary

- consumer boundary -> governance/module-manifest rules + UConsole readiness/status
- contract routing -> Contracts + LINK
- object mapping -> EDGE + Contracts
- identity preservation -> EDGE + LINK + UCDE + DB
- traceability preservation -> LINK + UCDE + DB
- external ingress -> EDGE Fleet

## 7. Non-scope

- no runtime implementation
- no API implementation
- no DB/schema implementation
- no contracts/schemas repository changes
- no EDGE/LINK/DB/Contracts source changes

## 8. Cleanup Rules

- retain one-adapter files as historical/deprecated records
- do not delete or move one-adapter directory in this task
- do not promote historical one-adapter files into active design gates

## 9. Next Task

`EDGE-FLEET-A1-CONSUMPTION-MODEL-DRAFT`
