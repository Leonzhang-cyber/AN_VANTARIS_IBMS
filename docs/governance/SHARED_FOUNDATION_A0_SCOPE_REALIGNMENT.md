# Shared Foundation A0 Scope Realignment

## 1. Decision

AN_VANTARIS_EDGE, AN_VANTARIS_LINK, and AN_VANTARIS_Contracts are shared VANTARIS foundation assets.

They are not:

- IBMS-private modules
- UFMS-private modules
- duplicate per-product implementations

## 2. Reason

VANTARIS ONE / IBMS and UFMS both require Edge, Link, and Contracts capabilities.
Duplicating them will create schema drift, protocol drift, ACK/DLQ drift, security boundary drift, and audit confusion.

## 3. Immediate Effect

Pause the following tasks as IBMS-private path:

- EDGE-A2-PROTOCOL-PLUGIN-DESCRIPTOR-BASELINE
- LINK-A0
- CONTRACTS-A2 as ONE-only
- any UFMS-side duplicated Edge/Link/Contracts implementation

All follow-up must first pass shared foundation scope.

## 4. Reclassification of Completed Work

- CONTRACTS-A0 -> Shared Contracts baseline draft
- CONTRACTS-A1 -> Shared Edge/Link contract schema draft
- EDGE-A0 -> Shared Edge skeleton draft
- EDGE-A0.1 -> Shared Edge package toolchain baseline
- EDGE-A1 -> Shared Edge connector registry dry-run

## 5. New Rule

No duplicate Edge / Link / Contracts implementation across VANTARIS ONE and UFMS.
