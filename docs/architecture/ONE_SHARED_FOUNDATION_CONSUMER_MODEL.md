# VANTARIS ONE Shared Foundation Consumer Model

Recommended data flow:

Device / BMS / FAS / ACS / CCTV / PLC / SCADA  
-> UFMS-led Shared EDGE  
-> UFMS-led Shared LINK  
-> Shared Contracts envelope  
-> VANTARIS ONE Adapter / Code API  
-> IBMS Core / MMS / ESG / CDE / Reports / Console

VANTARIS ONE consumer responsibilities:

- consume shared contract objects
- receive events/alarms/telemetry through approved API or adapter
- display Edge/Link health from shared foundation API
- map shared objects into IBMS Core/MMS/ESG/CDE contexts
- maintain product-specific dashboards and workflows
- not execute protocol drivers
- not own Link ACK/DLQ/retry runtime
- not redefine global contracts
