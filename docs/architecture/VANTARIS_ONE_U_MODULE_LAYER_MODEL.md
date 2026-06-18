# VANTARIS ONE U Module Layer Model

## 1. Purpose

Define the VANTARIS ONE three-layer architecture description using U-series module naming.

## 2. Foundation Layer (Reference-Only)

- AN_VANTARIS_Contracts
- AN_VANTARIS_EDGE
- AN_VANTARIS_LINK
- AN_VANTARIS_DB

This layer is consumed by VANTARIS ONE through approved boundaries and is not modified by this task.

## 3. Platform Layer

- UConsole
- Reports (Reporting Workspace / 报表工作台)
- Analytics
- Nexus AI Consumer

Platform layer provides status, reporting, analytics, shared AI service capability, and governance visibility while avoiding business-domain ownership.
Reports consumes standardized module references, events, evidence, status, metadata, and aggregated context, and does not directly connect to external systems.

## 4. Unified Business Modules

- UCore
- UMMS
- UESG
- UCDE
- UDOC

Business modules own domain context and consume standardized shared/foundation outputs through governance and module manifest boundaries.

## 5. Integration Ingress And Delivery Boundary

- integration ingress is handled by EDGE Fleet
- secure delivery is handled by LINK
- Shared Foundation includes Contracts, EDGE, LINK, and DB references
- ONE Adapter is removed from primary platform role and retained only as historical/deprecated record

## 6. Nexus AI Shared Service Note

Nexus AI is a shared service for all core modules, including UFMS.

## 7. Runtime Boundary

This model is architecture-only and does not create runtime implementations.

Foundation Layer is reference-only in this task. This task does not modify AN_VANTARIS_EDGE, AN_VANTARIS_LINK, AN_VANTARIS_DB, AN_VANTARIS_Contracts, contracts, or schemas.
