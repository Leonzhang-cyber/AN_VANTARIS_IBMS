# Module Manifest A0 Dependency Model

## 1. Foundation Layer

UFMS-led Shared Foundation:

- Contracts
- Edge
- Link

## 2. Consumer Boundary

ONE Adapter:

- validates contract/version
- preserves identity and traceability
- maps shared objects to ONE modules

## 3. Business Layer

- UCore consumes site/asset/event context
- UMMS consumes event/alarm/fault/work order context
- UESG consumes telemetry/meter/maintenance/energy context
- UDOC consumes data center telemetry/event/capacity/energy context
- UCDE consumes evidence/audit references

## 4. Platform Layer

UConsole displays:

- adapter status
- shared foundation health
- business module status
- audit/evidence status

## 5. Forbidden Dependencies

- business modules must not depend directly on Edge runtime
- business modules must not depend directly on Link runtime
- business modules must not import UFMS runtime
- UConsole must not bypass adapter/contracts
- modules must not redefine global Contracts
- UCDE must not become hidden data lake
- Reports/Analytics must not become shadow business owners
