# ONE Adapter A1 Foundation Consumer Boundary

## 1. Foundation Reference-Only Boundary

ONE Adapter consumes `AN_VANTARIS_Contracts`, `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, and `AN_VANTARIS_DB` as references only.

## 2. Business Module Consumption Path

UCore, UMMS, UESG, UCDE, and UDOC consume shared foundation references through ONE Adapter policies and mapping references.

## 3. Platform Linkage Path

UConsole, Reports, Analytics, and Nexus AI Consumer consume readiness and status references through ONE Adapter boundary context.

## 4. Routing and Mapping Draft

Defines docs-level routing policy for foundation-to-module reference consumption without generating executable contracts.

## 5. A1 Boundary

- no runtime adapter
- no API implementation
- no DB schema implementation
- no contracts/schemas modification
- no backend/frontend modifications

Foundation Layer remains reference-only in this task.
