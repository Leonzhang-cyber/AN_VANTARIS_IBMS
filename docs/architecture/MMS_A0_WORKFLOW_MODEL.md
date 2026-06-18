# MMS A0 Workflow Model

## 1. Alarm / Event to Work Order

Shared Foundation / IBMS Core / UFMS output  
-> ONE Adapter  
-> MMS triage  
-> Work Order draft  
-> Assignment  
-> Execution  
-> Evidence attachment  
-> Completion  
-> Closure report

## 2. Preventive Maintenance

Asset / schedule rule  
-> planned task  
-> assignment  
-> execution  
-> evidence  
-> completion  
-> history

## 3. Inspection

Inspection template  
-> inspection task  
-> field execution  
-> issue finding  
-> optional work order  
-> report

## 4. Future AI Assist

NexusAI or UFMS may suggest priority / cause / action, but MMS owns workflow state.

A0 does not create a real workflow engine.
A0 does not modify DB.
A0 does not create work order API.
A0 does not modify frontend menu.
