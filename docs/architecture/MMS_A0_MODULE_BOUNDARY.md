# MMS A0 Module Boundary

## 1. Purpose

MMS is the Maintenance Management System business module in VANTARIS ONE. It is responsible for maintenance planning, work orders, inspection, repair closure, and maintenance performance. It is not a shared foundation runtime.

## 2. MMS Owns

- maintenance work order lifecycle
- corrective maintenance workflow
- preventive maintenance workflow
- inspection task workflow
- maintenance schedule context
- technician / team assignment context
- SLA and response tracking
- spare parts usage reference
- maintenance history view
- handoff from alarm/event/fault to work order
- maintenance KPI and reporting view
- mobile field workflow boundary, future

## 3. MMS Does Not Own

- Edge protocol drivers
- Edge connector registry runtime
- Link ACK / DLQ / retry runtime
- global Contracts schema
- UFMS runtime
- UFMS correlation / RCA engine
- IBMS Core building operation dashboard
- CDE evidence chain core
- ESG carbon/accounting model
- shared machine identity runtime
- NexusAI model runtime
- DB schema ownership outside approved module boundary

## 4. Relationship With IBMS Core

MMS may receive operational context from IBMS Core:

- site
- building
- floor
- zone
- asset
- device
- alarm/event business view

But MMS owns maintenance action lifecycle.

## 5. Relationship With UFMS

MMS may consume UFMS fault intelligence output through ONE adapter and convert approved fault/action recommendations into work order context.
MMS must not import UFMS runtime source.

## 6. Relationship With Shared Foundation

MMS consumes shared telemetry/event/alarm/evidence references through ONE adapter and approved contracts.
