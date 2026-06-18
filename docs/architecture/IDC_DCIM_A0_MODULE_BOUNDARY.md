# IDC / DCIM A0 Module Boundary

## 1. Purpose

IDC / DCIM is the data center infrastructure operations business module in VANTARIS ONE. It covers data center space, rack/cabinet context, capacity, power, cooling, PUE, availability, data-center alarm business view, and operational risk view. It is not a shared foundation runtime.

## 2. IDC / DCIM Owns

- data center site / room / hall / zone / row / rack topology
- rack / cabinet / U-space operational view
- server / network / storage asset placement context
- power chain operational view
- UPS / PDU / RPP / rack PDU context
- cooling chain operational view
- CRAH / CRAC / in-row cooling / temperature / humidity context
- power capacity and load view
- cooling capacity and thermal risk view
- rack capacity / U-space / weight / power / network port capacity context
- PUE and energy efficiency view
- redundancy / resilience / availability view
- IDC alarm and incident business view
- IDC maintenance handoff to MMS
- IDC energy handoff to ESG
- IDC evidence handoff to CDE
- IDC SLA and uptime reporting context

## 3. IDC / DCIM Does Not Own

- Edge protocol drivers
- Edge connector registry runtime
- Link ACK / DLQ / retry runtime
- global Contracts schema
- UFMS runtime
- UFMS correlation / RCA engine
- MMS work order lifecycle
- ESG carbon accounting model
- CDE evidence chain core
- IBMS Core general building operations dashboard
- shared machine identity runtime
- NexusAI model runtime
- DB schema ownership outside approved module boundary

## 4. Relationship With IBMS Core

IDC / DCIM may consume building / floor / zone context from IBMS Core, but owns data center-specific topology and infrastructure operations.

## 5. Relationship With MMS

IDC / DCIM may create maintenance context for MMS, but MMS owns work order lifecycle.

## 6. Relationship With ESG

IDC / DCIM provides energy, PUE, cooling, UPS/PDU load and utility context to ESG, but ESG owns sustainability interpretation and carbon reporting.

## 7. Relationship With UFMS

IDC / DCIM may consume UFMS fault intelligence output for data center incidents, risk and RCA summary through ONE adapter.
IDC / DCIM must not import UFMS runtime source.

## 8. Relationship With Shared Foundation

IDC / DCIM consumes telemetry / event / alarm / health / evidence references through ONE adapter and approved contracts.
