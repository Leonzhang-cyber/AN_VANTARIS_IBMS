# ONE Adapter A0 Shared Foundation Interface

## 1. Purpose

VANTARIS ONE acts as a consumer and uses adapter/interface boundaries to consume UFMS-led Shared Foundation outputs. This stage defines architecture and interface planning only, without runtime implementation.

## 2. Interface Direction

Recommended direction:

UFMS-led Shared EDGE  
-> UFMS-led Shared LINK  
-> Shared Contracts Envelope  
-> VANTARIS ONE Adapter  
-> VANTARIS ONE Code / IBMS Core / MMS / ESG / CDE / Console

## 3. VANTARIS ONE Adapter Responsibilities

- receive normalized telemetry/event/alarm/evidence objects
- validate contract version
- validate tenant/project/site/source identity
- map shared objects into ONE business modules
- preserve traceId / messageId / correlationId
- expose consumer status to Console
- reject unsupported contract version
- record adapter-level audit event later

## 4. Adapter Must Not

- run protocol drivers
- own Edge connector lifecycle
- own Link ACK/DLQ/retry runtime
- redefine global contracts
- direct-write shared foundation DB
- copy UFMS runtime source
- copy UFMS schema/auth/login/seed/migration
- bypass approved contract boundary

## 5. Interface Types

Future interface types may include:

- REST pull
- REST push webhook
- message queue / event bus
- file batch import
- local lab dry-run fixture

This task does not implement any runtime interface.
