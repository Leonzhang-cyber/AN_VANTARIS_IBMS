# UFMS and VANTARIS ONE Shared Foundation Boundary

## 1. Correct Relationship

Device/System  
-> Shared EDGE  
-> Shared LINK  
-> VANTARIS ONE Code / UFMS Adapter  
-> UFMS Fault Intelligence / IBMS Core / CDE

## 2. UFMS Does Not Own

- protocol drivers
- Edge connector registry
- Link ACK/DLQ/retry
- global contracts
- global Edge normalized object schema
- global Link envelope schema

## 3. VANTARIS ONE Does Not Own Exclusively

- Edge runtime
- Link runtime
- Contracts
- UFMS fault intelligence internals

## 4. Adapter Boundary

UFMS integration must use:

- approved Contracts
- adapter API/event
- shared envelope
- shared identity/error/status definitions

No direct runtime/source/schema/auth/login/seed/migration copying.
