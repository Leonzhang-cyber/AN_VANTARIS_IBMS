# ESG A0 Module Boundary

## 1. Purpose

ESG is the Energy & Sustainability business module in VANTARIS ONE. It is responsible for energy consumption, carbon emission context, sustainable operation indicators, green building reporting, and compliance-oriented data views. It is not a shared foundation runtime.

## 2. ESG Owns

- energy consumption dashboard
- electricity / water / gas / chilled water consumption views
- carbon emission calculation context
- sustainability KPI view
- utility meter aggregation context
- baseline and benchmark view
- Green Mark / local sustainability reporting context
- ESG reporting workspace
- anomaly-to-energy-impact view
- maintenance-to-energy-impact view
- tenant / site / building sustainability summary
- carbon factor reference context, future

## 3. ESG Does Not Own

- Edge protocol drivers
- Edge connector registry runtime
- Link ACK / DLQ / retry runtime
- global Contracts schema
- UFMS runtime
- UFMS correlation / RCA engine
- IBMS Core operations dashboard
- MMS work order lifecycle
- CDE evidence chain core
- shared machine identity runtime
- NexusAI model runtime
- finance-grade carbon accounting certification engine
- DB schema ownership outside approved module boundary

## 4. Relationship With IBMS Core

ESG may consume site / building / zone / asset context from IBMS Core, but ESG owns sustainability and energy interpretation.

## 5. Relationship With MMS

ESG may consume maintenance outcome references from MMS to evaluate energy impact, but ESG does not own work order lifecycle.

## 6. Relationship With UFMS

ESG may consume UFMS fault intelligence output only when the fault has energy / sustainability impact.
ESG must not import UFMS runtime source.

## 7. Relationship With Shared Foundation

ESG consumes telemetry / meter readings / event / alarm / evidence references through ONE adapter and approved contracts.
