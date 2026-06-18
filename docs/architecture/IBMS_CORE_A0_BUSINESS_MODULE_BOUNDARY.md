# IBMS Core A0 Business Module Boundary

## 1. Purpose

IBMS Core (`ibms-core`) is the building operations business module in VANTARIS ONE. It is not a shared foundation runtime and does not own shared runtime responsibilities.

## 2. IBMS Core Owns

- building operation overview
- site / building / floor / zone operational views
- asset and device operational view
- alarm and event business view
- system status dashboard
- facility workflow context
- business reporting view
- operations KPIs
- user-facing workspace and navigation
- module-specific configuration

## 3. IBMS Core Does Not Own

- Edge protocol drivers
- Edge connector registry runtime
- Link ACK / DLQ / retry runtime
- global Contracts schema
- UFMS runtime
- UFMS correlation / RCA engine
- DB schema ownership outside approved module boundary
- shared machine identity runtime
- NexusAI model runtime
- CDE evidence chain core

## 4. Relationship With Shared Foundation

IBMS Core consumes:

- normalized telemetry
- events
- alarms
- edge health
- link delivery state
- evidence and audit references

through ONE adapter / approved contracts.

## 5. Relationship With UFMS

IBMS Core may consume UFMS fault intelligence output through adapter, but must not import UFMS runtime source.
