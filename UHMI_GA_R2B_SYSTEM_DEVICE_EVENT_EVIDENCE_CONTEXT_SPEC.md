# UHMI-GA-R2B System Device Event Evidence Context Spec

PASS marker: `UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS`

## Foundation

R2B is based on UHMI-GA-R2A. UHMI = Unified Human-Machine Interface. UHMI belongs to UConsole capability and remains under UConsole Workspace.

R2B is read-only. It is not independent HMI server infrastructure, not SCADA, and not a runtime control layer.

## System Context

System Context Panels include:

- Building Systems
- Facility Systems
- Security Systems
- Energy Systems
- Data Center Systems
- Utility Systems

Each system context includes systemId, systemName, category, healthStatus, visibleDevices, activeEvents, panelCount, evidenceCount, and readOnly = true.

## Device Context

Device Context table rows include deviceId, deviceName, systemName, location, status, lastSeen, eventCount, panelAvailable, and controlState = disabled/read-only.

## Mimic Panel Preview

Mimic Panel Preview is read-only. It includes panelId, panelName, systemName, previewType, status, readOnly, and controlsDisabled. It does not expose any executable controls.

## Event Context

Event Context rows include eventId, severity, title, sourceSystem, linkedDevice, timestamp, status, and evidenceLinked.

## Evidence Context

Evidence Context rows include evidenceId, type, linkedObject, source, timestamp, integrityStatus, and viewOnly.

## Guardrails

- Read-only Mode
- No Direct Device Control
- No Runtime Activation
- No DB Write
- No EDGE Command Execution
- No LINK Command Execution
- Future Control Path: `UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS`

