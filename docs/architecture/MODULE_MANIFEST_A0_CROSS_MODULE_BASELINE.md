# Module Manifest A0 Cross-module Baseline

## 1. Purpose

Define the VANTARIS ONE cross-module manifest baseline.

## 2. Module Families

Platform / Consumer:

- ONE Adapter
- Console

Business Modules:

- IBMS Core
- MMS
- ESG
- IDC / DCIM
- CDE

Supporting / Future:

- Reports
- Analytics
- Nexus AI Consumer

Shared Foundation:

- Contracts
- Edge
- Link

## 3. Boundary Summary

- ONE Adapter consumes Shared Foundation.
- IBMS Core owns building operations context.
- MMS owns maintenance workflow context.
- ESG owns energy and sustainability interpretation.
- IDC/DCIM owns data center infrastructure operations context.
- CDE owns evidence and traceability context.
- Console owns platform health and governance view.
- Reports consumes approved module outputs.
- Analytics consumes approved module outputs.
- Nexus AI Consumer is future and does not own model runtime yet.

## 4. Runtime Boundary

This task does not create runtime.
